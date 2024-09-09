package entity;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public class Device { 
	
	public int id;
	public int capacity;
	public int resourcesLeft;
	public List<VNF> allocatedVNFs;
	public List<Integer> preferences; // List of VNF IDs ranked by resource usage (ascending)

    public Device(int id, int capacity, int usedResources) {
        this.id = id;
        this.capacity = capacity;
        this.resourcesLeft = capacity - usedResources;
        this.allocatedVNFs = new ArrayList<>();
        this.preferences = new ArrayList<>();
    }

    public void calculatePreferences(List<VNF> vnfs) {
        // Calculate preferences based on VNFs that utilize maximum resources from available resources
        List<VNF> sortedVNFs = new ArrayList<>();
        for (VNF vnf : vnfs) {
            if (hasCapacityFor(vnf)) {
                sortedVNFs.add(vnf);
            }
        }
        sortedVNFs.sort(Comparator.comparingInt(v -> -v.resourceRequirement)); // Sort VNFs by resource requirement descending
        for (VNF vnf : sortedVNFs) {
            preferences.add(vnf.id);
        }
    }

    public boolean hasCapacityFor(VNF vnf) {
        return resourcesLeft >= vnf.resourceRequirement;
    }

    public void allocateVNF(VNF vnf) {
        allocatedVNFs.add(vnf);
        resourcesLeft -= vnf.resourceRequirement;
    }

	@Override
	public String toString() {
		return "Device [id=" + id + ", capacity=" + capacity + ", resourcesLeft=" + resourcesLeft + ", ] \n";
	}
    
    

}
