from app_utils import add_new_node_to_config, add_new_edge_to_config, add_new_activity_to_config


class Graph:
    screens = []
    edges = []
    activity_count = {}
    app = ""
    device = ""
    mode = ""

    def __init__(self, app, device, mode):
        self.app = app
        self.device = device
        self.mode = mode

    def addScreen(self, screen):
        self.screens.append(screen)
        add_new_node_to_config(self.app, self.device, self.mode, screen)

    def addEdge(self, edge):
        for discoveredEdge in self.edges:
            if edge.src == discoveredEdge.src and edge.dest == discoveredEdge.dest:
                return
        self.edges.append(edge)
        add_new_edge_to_config(self.app, self.device, self.mode, edge)

    def checkScreenExisted(self, screenHash):
        for screen in self.screens:
            if screen.nodeHash == screenHash:
                return True
        return False

    def getScreenFromExisted(self, screenHash):
        for screen in self.screens:
            if screen.nodeHash == screenHash:
                return screen

    def __str__(self):
        return "Graph: \n" + "Nodes: \n" + '\n '.join(map(str, self.screens)) + "\n" + "Edges: \n" + '\n '.join(
            map(str, self.edges)) + "\n" + str(self.activity_count)

    def getNodes(self):
        return "Nodes: \n" + '\n '.join(map(str, self.screens))

    def getCurrentActivityDictAsString(self):
        str = ""
        for x in self.activity_count:
            str += (x + ":")

    def logNodeAndEdgeToConfig(self):
        for edge in self.edges:
            add_new_edge_to_config(self.app, self.device, self.mode, edge)
        for node in self.screens:
            add_new_node_to_config(self.app, self.device, self.mode, node)


    def getActivityStoringName(self, activity):
        if activity in self.activity_count.keys():
            self.activity_count[activity] += 1
            return activity + str(self.activity_count[activity])
        else:
            self.activity_count[activity] = 1
            add_new_activity_to_config(self.app, self.device, self.mode, activity)
            return activity + str(1)

class Screen:
    screenCount = 0

    def __init__(self, nodeInfo, nodeHash, nodeActivityName, clickableViews):
        self.nodeInfo = nodeInfo
        self.nodeHash = nodeHash
        self.nodeActivityName = nodeActivityName
        self.clickableViews = clickableViews
        self.clickedViews = []

    def addToClickedView(self, clickableView):
        self.clickedViews.append(clickableView)

    def __str__(self):
        return "Node: " + self.nodeActivityName + " | " + self.nodeHash + " | " + str(
            len(self.clickedViews)) + "/" + str(len(self.clickableViews))


class Edge:
    def __init__(self, clickedBtnHash, src=None, dest=None):
        self.src = src
        self.dest = dest
        self.clickedBtnHash = clickedBtnHash

    def __str__(self):
        return "Edge: " + self.src + " -> " + self.dest
