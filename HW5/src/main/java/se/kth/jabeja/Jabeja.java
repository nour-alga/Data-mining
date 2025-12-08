package se.kth.jabeja;

import org.apache.log4j.Logger;
import se.kth.jabeja.config.Config;
import se.kth.jabeja.config.NodeSelectionPolicy;
import se.kth.jabeja.io.FileIO;
import se.kth.jabeja.rand.RandNoGenerator;

import java.io.File;
import java.io.IOException;
import java.util.*;

public class Jabeja {
    final static Logger logger = Logger.getLogger(Jabeja.class);
    private final Config config;
    private final HashMap<Integer/* id */, Node/* neighbors */> entireGraph;
    private final List<Integer> nodeIds;
    private int numberOfSwaps;
    private int round;
    private float T;
    private boolean resultFileCreated = false;

    // Parameters for SA restart
    private int lastEdgeCut = Integer.MAX_VALUE;
    private int convergenceCounter = 0;
    private static final int CONVERGENCE_THRESHOLD = 50; // Number of rounds without improvement
    private static final int RESTART_INTERVAL = 200; // Restart every N rounds after convergence

    // -------------------------------------------------------------------
    public Jabeja(HashMap<Integer, Node> graph, Config config) {
        this.entireGraph = graph;
        this.nodeIds = new ArrayList<>(entireGraph.keySet());
        this.round = 0;
        this.numberOfSwaps = 0;
        this.config = config;
        this.T = config.getTemperature();
    }

    // -------------------------------------------------------------------
    public void startJabeja() throws IOException {
        for (round = 0; round < config.getRounds(); round++) {
            for (int id : entireGraph.keySet()) {
                sampleAndSwap(id);
            }

            // one cycle for all nodes have completed.
            // reduce the temperature
            saCoolDown();
            report();
        }
    }

    /**
     * Simulated annealing cooling function
     */
    private void saCoolDown() {
        // exponential cooling
        T = (float) (T * config.getDelta()); // cast to float to fix compilation
        if (T < 1) {
            T = 1;
        }

        // for bonus part: restart mechanism after stagnation
        if (convergenceCounter >= CONVERGENCE_THRESHOLD) {
            logger.info("*** RESTARTING Simulated Annealing at round " + round + " ***");
            T = (float) (config.getTemperature() * 1.5); // restart with 1.5x initial temp
            convergenceCounter = 0;
        }
    }

    /**
     * Sample and swap algorithm at node p
     */
    private void sampleAndSwap(int nodeId) {
        Node partner = null;
        Node nodep = entireGraph.get(nodeId);

        if (config.getNodeSelectionPolicy() == NodeSelectionPolicy.HYBRID
                || config.getNodeSelectionPolicy() == NodeSelectionPolicy.LOCAL) {
            Integer[] neighbourIds = getNeighbors(nodep);
            partner = findPartner(nodeId, neighbourIds);
        }

        if (partner == null && config.getNodeSelectionPolicy() == NodeSelectionPolicy.HYBRID
                || config.getNodeSelectionPolicy() == NodeSelectionPolicy.RANDOM) {
            Integer[] sampleIds = getSample(nodeId);
            partner = findPartner(nodeId, sampleIds);
        }

        if (partner == null) {
            return;
        }

        // swap the colors
        int tempColor = nodep.getColor();
        nodep.setColor(partner.getColor());
        partner.setColor(tempColor);
        numberOfSwaps++;
    }

    /**
     * Find partner using simulated annealing acceptance probability
     */
    public Node findPartner(int nodeId, Integer[] nodes) {
        Node nodep = entireGraph.get(nodeId);
        Node bestPartner = null;
        double highestBenefit = 0;

        for (Integer candidateId : nodes) {
            Node candidate = entireGraph.get(candidateId);

            int degreeNodepBefore = getDegree(nodep, nodep.getColor());
            int degreeCandidateBefore = getDegree(candidate, candidate.getColor());

            int degreeNodepAfter = getDegree(nodep, candidate.getColor());
            int degreeCandidateAfter = getDegree(candidate, nodep.getColor());

            // benefit = new_cost - old_cost
            double benefit = (degreeNodepAfter + degreeCandidateAfter)
                    - (degreeNodepBefore + degreeCandidateBefore);

            // for bonus part: adaptive acceptance probability
            double neighborFactor = 1.0 + Math.log(nodep.getNeighbours().size() + 1);
            double adaptiveFactor = 1.0 + (convergenceCounter / 50.0);
            double acceptanceProbability = Math.exp(benefit / (T * neighborFactor * adaptiveFactor));
            double random = Math.random();

            if (benefit > 0 || acceptanceProbability > random) {
                if (benefit > highestBenefit) {
                    highestBenefit = benefit;
                    bestPartner = candidate;
                }
            }
        }

        return bestPartner;
    }

    /**
     * The degree on the node based on color
     */
    private int getDegree(Node node, int colorId) {
        int degree = 0;
        for (int neighborId : node.getNeighbours()) {
            Node neighbor = entireGraph.get(neighborId);
            if (neighbor.getColor() == colorId) {
                degree++;
            }
        }
        return degree;
    }

    private Integer[] getSample(int currentNodeId) {
        int count = config.getUniformRandomSampleSize();
        int rndId;
        int size = entireGraph.size();
        ArrayList<Integer> rndIds = new ArrayList<>();

        while (true) {
            rndId = nodeIds.get(RandNoGenerator.nextInt(size));
            if (rndId != currentNodeId && !rndIds.contains(rndId)) {
                rndIds.add(rndId);
                count--;
            }

            if (count == 0)
                break;
        }

        Integer[] ids = new Integer[rndIds.size()];
        return rndIds.toArray(ids);
    }

    private Integer[] getNeighbors(Node node) {
        ArrayList<Integer> list = node.getNeighbours();
        int count = config.getRandomNeighborSampleSize();
        int rndId;
        int index;
        int size = list.size();
        ArrayList<Integer> rndIds = new ArrayList<>();

        if (size <= count)
            rndIds.addAll(list);
        else {
            while (true) {
                index = RandNoGenerator.nextInt(size);
                rndId = list.get(index);
                if (!rndIds.contains(rndId)) {
                    rndIds.add(rndId);
                    count--;
                }

                if (count == 0)
                    break;
            }
        }

        Integer[] arr = new Integer[rndIds.size()];
        return rndIds.toArray(arr);
    }

    private void report() throws IOException {
        int grayLinks = 0;
        int migrations = 0;
        int size = entireGraph.size();

        for (int i : entireGraph.keySet()) {
            Node node = entireGraph.get(i);
            int nodeColor = node.getColor();
            ArrayList<Integer> nodeNeighbours = node.getNeighbours();

            if (nodeColor != node.getInitColor()) {
                migrations++;
            }

            if (nodeNeighbours != null) {
                for (int n : nodeNeighbours) {
                    Node p = entireGraph.get(n);
                    int pColor = p.getColor();

                    if (nodeColor != pColor)
                        grayLinks++;
                }
            }
        }

        int edgeCut = grayLinks / 2;

        // Track convergence for restart mechanism
        if (edgeCut >= lastEdgeCut) {
            convergenceCounter++;
        } else {
            convergenceCounter = 0;
        }
        lastEdgeCut = edgeCut;

        logger.info("round: " + round +
                ", edge cut:" + edgeCut +
                ", swaps: " + numberOfSwaps +
                ", migrations: " + migrations +
                ", T: " + String.format("%.4f", T));

        saveToFile(edgeCut, migrations);
    }

    private void saveToFile(int edgeCuts, int migrations) throws IOException {
        String delimiter = "\t\t";
        String outputFilePath;

        File inputFile = new File(config.getGraphFilePath());
        outputFilePath = config.getOutputDir() +
                File.separator +
                inputFile.getName() + "_" +
                "NS" + "_" + config.getNodeSelectionPolicy() + "_" +
                "GICP" + "_" + config.getGraphInitialColorPolicy() + "_" +
                "T" + "_" + config.getTemperature() + "_" +
                "D" + "_" + config.getDelta() + "_" +
                "RNSS" + "_" + config.getRandomNeighborSampleSize() + "_" +
                "URSS" + "_" + config.getUniformRandomSampleSize() + "_" +
                "A" + "_" + config.getAlpha() + "_" +
                "R" + "_" + config.getRounds() + ".txt";

        if (!resultFileCreated) {
            File outputDir = new File(config.getOutputDir());
            if (!outputDir.exists()) {
                if (!outputDir.mkdir()) {
                    throw new IOException("Unable to create the output directory");
                }
            }
            String header = "# Migration is number of nodes that have changed color.";
            header += "\n\nRound" + delimiter + "Edge-Cut" + delimiter + "Swaps" + delimiter + "Migrations" + delimiter
                    + "Skipped" + "\n";
            FileIO.write(header, outputFilePath);
            resultFileCreated = true;
        }

        FileIO.append(round + delimiter + (edgeCuts) + delimiter + numberOfSwaps + delimiter + migrations + "\n",
                outputFilePath);
    }
}
