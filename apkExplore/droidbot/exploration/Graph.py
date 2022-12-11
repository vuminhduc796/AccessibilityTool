class Graph:
    screens = []
    edges = []

    def addScreen(self, screen):
        self.screens.append(screen)

    def addEdge(self, edge):
        for discoveredEdge in self.edges:
            if edge.src == discoveredEdge.src and edge.dest == discoveredEdge.dest:
                return
        self.edges.append(edge)

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
            map(str, self.edges))


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
