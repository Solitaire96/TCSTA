import xml.etree.ElementTree as ET
import re

from TA import *

def parseUppaalXML(file):
    invRegex = re.compile("([a-zA-Z]+)([<>=]+)([0-9]+)")

    tree = ET.parse(file)
    root = tree.getroot()

    TAs = []

    for template in root.findall("template"):
        TA = TimedAutomaton()

        idToName = {}

        for state in template.findall("location"):
            stateID = state.attrib.get("id")
            name = state.find("name").text if state.find("name") is not None else stateID

            idToName[stateID] = name

            inv = None

            for label in state.findall("label"):
                if label.attrib.get("kind") == "invariant":
                    inv = invRegex.match(label.text).groups()
                    inv = Invariant(inv[0], inv[1], inv[2])
            
            TA.addState(name, inv)
        
        for transition in template.findall("transition"):
            source = idToName[transition.find("source").attrib.get("ref")]
            dest = idToName[transition.find("target").attrib.get("ref")]

            guard = None

            for label in transition.findall("label"):
                if label.attrib.get("kind") == "guard":
                    guard = invRegex.match(label.text).groups()
                    guard = Invariant(guard[0], guard[1], int(guard[2]))
                elif label.attrib.get("kind") == "assignment":
                    reset = int(invRegex.match(label.text).groups()[2])
                    TA.states[dest].setReset(reset)
                

            TA.addTransition(source, dest, guard)

        initID = template.find("init").attrib.get("ref")
        TA.setInit(idToName[initID])

        TAs.append(TA)
    
    return TAs




def main():
    TA = parseUppaalXML('tcn_model.xml')[0]

    print TA

    TCN = TA.toTCN()
    print ( TCN )
    print ( TCN.findMinimalNetwork() )
    print ( TCN.pathExists("a", "d", ">=", 18) )
    print ( TCN.forAllPaths("a", "d", ">=", 18) )
    print ( TCN.forAllPaths("a", "d", ">=", 11) )
    print ( TCN.forAllPaths("a", "d", ">=", 12) )
    print 


    print ( TCN.pathExists("a", "c", "<", 5) )
    print ( TCN.pathExists("a", "c", "<", 15) )
    print ( TCN.forAllPaths("a", "c", "<", 15) )





    


    



main()