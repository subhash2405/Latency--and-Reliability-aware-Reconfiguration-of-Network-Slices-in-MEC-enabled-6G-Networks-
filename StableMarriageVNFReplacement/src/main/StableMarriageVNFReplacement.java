package main;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Random;

import entity.Device;
import entity.VNF;

public class StableMarriageVNFReplacement {
	
	public static void main(String[] args) {
        int n = 5; // Number of physical devices
        Random random = new Random();

        // Generate random distance matrix
        int[][] distanceMatrix = new int[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < n; j++) {
                if (i != j) {
                    distanceMatrix[i][j] = random.nextInt(100) + 1;
                }
            }
        }

        // Initialize devices with random capacities and used resources
        List<Device> devices = new ArrayList<>();
        for (int i = 0; i < n; i++) {
        	int capacity = random.nextInt(10) + 50; //Random capacity of devices
            int usedResources = 0;
            devices.add(new Device(i, capacity, usedResources));
        }
       

        // Initialize VNFs and allocate them randomly to devices
        List<VNF> allVNFs = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            int numVNFs = random.nextInt(5) + 1;
            for (int j = 0; j < numVNFs; j++) {
                int resourceRequirement = random.nextInt(20) + 10;
                VNF vnf = new VNF(allVNFs.size(), resourceRequirement);
                if(devices.get(i).resourcesLeft >= resourceRequirement) {
                	allVNFs.add(vnf);
                	devices.get(i).allocateVNF(vnf);
                	vnf.device = devices.get(i);
                }
            }
        }
        
        System.out.println("Devices are: "+devices);
        System.out.println("\n");

        // Simulate device failure
        Device failedDevice = devices.remove(random.nextInt(devices.size()));
        System.out.println("Failed device : "+failedDevice.id);
        System.out.println("VNFs in it: "+failedDevice.allocatedVNFs);
        
        List<VNF> displacedVNFs = new ArrayList<>(failedDevice.allocatedVNFs);

        // Calculate preferences for VNFs and remaining devices
        for (VNF vnf : displacedVNFs) {
            vnf.calculatePreferences(devices, distanceMatrix);
        }
        for (Device device : devices) {
            device.calculatePreferences(displacedVNFs);
        }

        // Perform Stable Marriage to find VNF placement
        Map<VNF, Device> matching = stableMarriage(displacedVNFs, devices);

        // Output results
        for (VNF vnf : matching.keySet()) {
            Device device = matching.get(vnf);
            System.out.println("VNF " + vnf.id + " with resource requirement " + vnf.resourceRequirement + " is allocated to Device " + device.id);
        }
    }

    public static Map<VNF, Device> stableMarriage(List<VNF> vnfs, List<Device> devices) {
        Map<VNF, Device> matching = new HashMap<>();
        Queue<VNF> freeVNFs = new LinkedList<>(vnfs);

        Map<Device, VNF> currentMatches = new HashMap<>();
        while (!freeVNFs.isEmpty()) {
            VNF vnf = freeVNFs.poll();
            for (Integer deviceId : vnf.preferences) {
                Device device = devices.stream().filter(d -> d.id == deviceId).findFirst().get();
                if (device.hasCapacityFor(vnf)) {
                    if (!currentMatches.containsKey(device)) {
                        device.allocateVNF(vnf);
                        matching.put(vnf, device);
                        currentMatches.put(device, vnf);
                        break;
                    } else {
                        VNF currentVNF = currentMatches.get(device);
                        if (device.preferences.indexOf(vnf.id) < device.preferences.indexOf(currentVNF.id)) {
                            currentMatches.remove(device);
                            matching.remove(currentVNF);
                            freeVNFs.add(currentVNF);
                            device.allocateVNF(vnf);
                            matching.put(vnf, device);
                            currentMatches.put(device, vnf);
                            break;
                        }
                    }
                }
            }
        }

        return matching;
    }

}
