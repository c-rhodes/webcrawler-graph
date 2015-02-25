from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader

import matplotlib.pyplot as plt
import networkx as nx

path = str(Path(__file__).parent)
jinja_env = Environment(loader=FileSystemLoader(path))

def main():
    # A graph of the internet we construct below
    internet_graph = nx.DiGraph()
    # The starting page we begin 'crawling' from
    start_page = 'page1.html'
    
    # Construct the 'internet' with 10 apges
    internet = build_internet(build_pages(10))
    crawl(internet_graph, start_page, internet)
    ranked_pages = pagerank(internet_graph)

    # Build a dictionary of labels key=node, value=label (pagename with pagerank as str)
    node_labels = {
        node: node.split('.html')[0] + '(PRank={})'.format(
            internet_graph.node[node]['pagerank']
        ) for node in ranked_pages
    }
    draw_graph(internet_graph, node_labels=node_labels, node_text_size=10)


def draw_graph(graph, labels=None, node_labels=None, graph_layout='spring',
               node_size=1600, node_color='green', node_alpha=0.3,
               node_text_size=12, edge_color='black', edge_alpha=0.3,
               edge_thickness=1, edge_text_pos=0.3, text_font='sans-serif'):

    G = nx.Graph()

    for edge in graph.edges():
        G.add_edge(edge[0], edge[1])

    graph_pos = getattr(nx, graph_layout + '_layout')(G, k=0.5, weight='pagerank')
    node_size = [graph.node[node]['pagerank']*200 for node in graph.nodes()]
    nx.draw_networkx_nodes(G, graph_pos, node_size=node_size,
                           alpha=node_alpha, node_color=node_color)
    nx.draw_networkx_edges(G, graph_pos, width=edge_thickness,
                          alpha=edge_alpha, edge_color=edge_color)
    nx.draw_networkx_labels(G, graph_pos, node_labels, font_size=node_text_size,
                            font_family=text_font)
    
    title_font = dict(fontname='Helvetica', color='k', fontweight='bold', fontsize=14)
    plt.title('Graph of the Internet', title_font)

    plt.text(0.5, 0.97, 'Node size ≈ PageRank',
             horizontalalignment='center',
             transform=plt.gca().transAxes)
    
    plt.axis('off')
    plt.show()
                           

def pagerank(graph):
    """A pages rank is determined by the number of pages that point to it."""
    return sorted(graph, key=lambda node: graph.node[node]['pagerank'], reverse=True)

def crawl(graph, page, internet):
    """ Given a Graph, starting page, and
    dataset (the 'internet') recursively 
    parse the links in the html constructing
    a graph.
    """
    if page not in graph:
        graph.add_node(page, pagerank=0)
    else:
        return

    try:
        soup = BeautifulSoup(internet[page])
    except KeyError:
        return

    for link in soup.findAll('a'):
        link = link.get('href')
        crawl(graph, link, internet)
        graph.add_edge(page, link)
        if link != page:
            graph.node[link]['pagerank'] += 1

def build_internet(pages):
    """Build a dict (the 'internet') from a list of pages with key=page name, val=html."""
    internet = dict()
    for page_no, page in enumerate(pages, 1):
        internet['page{}.html'.format(page_no)] = page
    return internet

def build_pages(n):
    """Build html files with Jinja from a
    base template. n pages are produced with the 1st
    page referencing page2, and page2 referencing pages
    1 and 3, and page3 referencing pages 1, 2 and 4, 
    and so on. This algorithm is to demonstrate the
    pagerank algorithm.
    """
    pages = list()
    template = jinja_env.get_template('template.html')
    # i is the current page and we want the current
    # page to point to the next page and all of the 
    # pages before it if it isn't the last page (page n).
    # Add 1 to n because we start from 1.
    for i in range(1, n + 1):
        links = list(range(1, i))
        # Add the next page if (i + 1) if it isn't the last page (n + 1)
        links += [i + 1] if i + 1 != n + 1 else []
        context = dict(title='Page{}'.format(i), links=links)
        pages.append(template.render(context))

    return pages


if __name__ == '__main__':
    main()
