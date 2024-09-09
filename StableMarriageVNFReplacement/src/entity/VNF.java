package entity;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class VNF {

	public int id;
	public int resourceRequirement;
	public Device device; // The device to which this VNF is currently assigned
	public List<Integer> preferences; // List of device IDs ranked by migration cost

	public VNF(int id, int resourceRequirement) {
		this.id = id;
		this.resourceRequirement = resourceRequirement;
		this.preferences = new ArrayList<>();
	}

	public void calculatePreferences(List<Device> devices, int[][] distanceMatrix) {
		// Calculate preferences based on migration cost (distance) if resource
		// requirement matches
		for (Device device : devices) {
			if (device.hasCapacityFor(this)) {
				preferences.add(device.id);
			}
		}
		// Sort preferences by migration cost (distance) from the current device
		preferences.sort(Comparator.comparingInt(d -> distanceMatrix[this.device.id][d]));
	}

	@Override
	public String toString() {
		return "VNF [id=" + id + ", resourceRequirement=" + resourceRequirement + ", preferences=" + preferences + "]\n";
	}
	
	

}
