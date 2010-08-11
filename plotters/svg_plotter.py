
def plot(graph, position, f):
    f.write('<?xml version="1.0" standalone="no"?>\n')
    f.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
    f.write('<svg width="100%" height="100%" version="1.1" xmlns="http://www.w3.org/2000/svg">\n')

    for e in graph.edges():
        u,v = position[e[0]]
        x,y = position[e[1]]
        f.write('<line x1="%s" y1="%s" x2="%s" y2="%s" style="stroke:rgb(99,99,99);stroke-width:3"/>' % (u,v,x,y))

    for v in graph.vertices():
        f.write('<circle cx="%s" cy="%s" r="5" stroke="black" stroke-width="2" fill="blue"/>' % position[v])

    f.write('</svg>\n')
