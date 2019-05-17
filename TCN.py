class TCN:
    def __init__(self):
        self.events  = {}

    def __str__(self):
         return str(self.events.items()) + "\n"

    def addEvent(self, label):
        self.events[label] = []

    def addEdge(self, source, dest, constr, isPrimitive = False):
        edge = Edge(source, dest, constr, isPrimitive)
        self.events[source].append(edge)


    def removeEdge(self, source, dest):
        edges = self.events[source]
        rem = None
        for edge in edges:
            if edge.dest == dest:
                rem = edge
        
        if rem is not None:
            edges.remove(rem)

    def getEdge(self, source, dest):
        edges = self.events[source]
        for edge in edges:
            if edge.dest == dest:
                return edge


    def topSort(self):
        def visit(event, s):
            if event not in s:
                for e in self.events[event]:
                    visit(e.dest, s)
                s.append(event)

        s = []
        for event in self.events.keys():
            visit(event, s)

        s.reverse()
        return s

    def topGreater(self, event1, event2):
        sort = self.topSort()

        return sort.index(event1) <= sort.index(event2)


    def getPath(self, source, dest):
        path = Path(source, dest)

        n = source

        while n != dest:
            path.addNode(n)
            n = self.next.get((n, dest))


        return path



    def convertToTAPath(self, source, dest):
        #for source in self.events.keys():
            #for dest in self.events.keys():
                #paths[(source, dest)] = self.getFullPath(source, dest)

        return None


    def findMinimalDistances(self):
        next = {}
        dist = {}

        # initialize the distance matrix
        for source in self.events.keys():
            for dest in self.events.keys():
                if source == dest:
                    dist[(source, dest)] = 0
                else:
                    dist[(source, dest)] = Constraint.inf

                next[(source, dest)] = dest

        # add the weighted distances from the TCN
        for source in self.events.keys():
            edges = self.events[source]
            for edge in edges:
                dest = edge.dest
                lower = edge.constr.lower
                upper = edge.constr.upper
                dist[(source, dest)] = upper
                dist[(dest, source)] = -lower

                
        


        # Floyd-Warshall algorithm
        for mid in self.events.keys():
            for source in self.events.keys():
                for dest in self.events.keys():
                    if dist[(source, mid)] + dist[(mid, dest)] < dist[(source, dest)]:
                        dist[(source, dest)] = dist[(source, mid)] + dist[(mid, dest)]
                        next[(source, dest)] = next[(source, mid)]

                    #check for negative cycles
                    # add in negative cycle return in bad case
                    if source == dest and dist[(source, dest)] < 0:
                        return None

        print next

        #paths = self.expandPaths(paths)

        self.next = next


        return dist


    def isConsistent(self):
        return self.findMinimalDistances() is not None

    def findMinimalNetwork(self):
        dist = self.findMinimalDistances()

        if dist is None:
            return None

        tcn = TCN()

        for event in self.events.keys():
            tcn.addEvent(event)

        for event1 in self.events.keys():
            for event2 in self.events.keys():
                if tcn.getEdge(event1, event2) is None and tcn.getEdge(event2, event1) is None:

                    # these should be assigned with respect to topological edge orientations

                    lower = -min( dist[(event1, event2)], dist[(event2, event1)] )
                    upper = max( dist[(event1, event2)], dist[(event2, event1)] )

                    if lower == upper:
                        if( self.topGreater(event1, event2) ):
                            tcn.addEdge(event1, event2, Constraint(lower, upper))
                        else:
                            tcn.addEdge(event2, event1, Constraint(lower, upper))
                    
                    elif dist[(event1, event2)] >= dist[(event2, event1)]:
                        tcn.addEdge(event1, event2, Constraint(lower, upper))
                    else:
                        tcn.addEdge(event2, event1, Constraint(lower, upper))

        self.minNetwork = tcn

        return tcn

    def pathExists(self, source, dest, expr, time):
        if not hasattr(self, 'minNetwork'):
            self.findMinimalNetwork()

        source = source + "-b"
        dest = dest + "-b"

        if self.minNetwork.getEdge(source, dest) is None:
            return False, None

        constr  = self.minNetwork.getEdge(source, dest).constr

        lower = constr.lower
        upper = constr.upper


        if expr == "<" or expr == "<=":
            exists = eval(str(lower) + expr + str(time))

            if exists:
                return True, self.getPath(source, dest)

        elif expr == ">" or expr == ">=":
            if upper == Constraint.inf:
                exists = True
            else: 
                exists = eval(str(upper) + expr + str(time))

            if exists:
                return True, self.getPath(source, dest)

        return False, None

    def forAllPaths(self, source, dest, expr, time):
        if not hasattr(self, 'minNetwork'):
            self.findMinimalNetwork()

        source = source + "-b"
        dest = dest + "-b"

        if self.minNetwork.getEdge(source, dest) is None:
            return False, None

        constr  = self.minNetwork.getEdge(source, dest).constr

        lower = constr.lower
        upper = constr.upper


        if expr == "<" or expr == "<=":
            if upper == Constraint.inf:
                exists = False
            else: 
                exists = eval(str(upper) + expr + str(time))

            if exists:
                return True, self.getPath(source, dest)

        elif expr == ">" or expr == ">=":
            exists = eval(str(lower) + expr + str(time))

            if exists:
                return True, self.getPath(source, dest)

        return False, None


    def setInit(self, init):
        self.init = init

class Constraint:
    epsilon = 1e-9
    inf = float("inf")

    def __init__(self, lower = 0, upper = inf):
        self.lower = lower
        self.upper = upper

    def isTrivialConstraint(self):
        return self.lower == 0 and (self.upper == 0 or self.upper is self.inf)

    def getTimeAdjustedConstraint(self, time):
        l = max(0, self.lower - time)
        u = max(0, self.upper - time)
        
        return Constraint(l, u)

    def intersect(self, other):
        lower = max(self.lower, other.lower)
        upper = min(self.upper, other.upper)
        if lower <= upper:
            return Constraint(lower, upper)
        else:
            return None

    def compose(self, other):
        return Constraint(self.lower + other.lower, self.upper + other.upper)

    def __str__(self):
        return "[" + str(self.lower) + "," + str(self.upper) + "]"

    def __repr__(self):
        return str(self)



class Edge:
    def __init__(self, source, dest, constr = None, isPrimitive = False):
        self.source = source
        self.dest = dest
        self.constr = constr
        self.isPrim = isPrimitive


    def __str__(self):
        return "(" + self.source + "->" + self.dest + ", " + str(self.constr) + ")"

    def __repr__(self):
        return str(self)


class Path:
    def __init__(self, source, dest):
        self.source = source
        self.dest = dest
        self.path = [source, dest]

    def addNode(self, node):
        if node != self.source and node != self.dest:
            self.path.pop()
            self.path.append(node)
            self.path.append(self.dest)

    def __str__(self):
        return "->".join(self.path)

    def __repr__(self):
        return str(self)