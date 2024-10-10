
# Latency and Relaibility aware reconfiguration of netowrk slices in 6G architecture

A brief description of what this project does.

We try to find suitable servers to deploy the VNF's of failed servers. We have implemented 4 different algorithms to achieve this and each of these algorithms try to achieve the same objective with different heuristics and approaches.

The main.py file in the Simulations\entity folder contains 4 functions:

1.) bestfit_algo_cost(failing_servers) - Implements bestfit algo with respect to cost \
2.) bestfit_algo_resources(failing_servers) - Implements bestfit with respect to resources \
3.) nearest_hop_algo(failing_servers) - Implements Nearest_Hop Algo.
4.) handle_server_failure(failing_servers) - Implements Stable Matching Algo.

The results of these simulations keep getting updated to the results.csv file in the entity folder and we can also get a detailed report in the simulation_output.txt file

