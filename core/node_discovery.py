'''
"Node discovery". *Hack*
This implementation of p2p node discovery takes
advantage of docker and information sharing through
environment variables. REAL discovery should probably happen
through DNS.
'''

# returns a list of node addresses
def discoverNodes():
    import os
    import random
    numNodes, serviceName = int(os.environ['NUMNODES']), os.environ['SERVICENAME']
    if numNodes is None or serviceName is None:
        print("Node discovery could not be performed.")
        return []
    return list(map(lambda i: serviceName + '_' + str(i), list(range(1, numNodes + 1))))
