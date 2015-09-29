"""
Dependencies:
- Python 3.4+
- lxml 3.4.4
"""

from datetime import datetime

from lxml import etree
import csv

XML_FILE_PATH = "dblp.xml" # Requires dblp.dtd also
ALL_ELEM = set(["article", "inproceedings", "proceedings", "book",
                "incollection", "phdthesis", "mastersthesis", "www"])

def emit_log(message):
    """
    Produce a log with current time.
    """
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)

def _clear_element(element):
    """
    Free up memery for temparily element tree after processing an element.
    """
    element.clear()
    while element.getprevious() is not None:
        del element.getparent()[0]

def _context(xmlfile=XML_FILE_PATH):
    """
    Create a context iterable of (event, element) pairs for processing.
    """
    return etree.iterparse(source=xmlfile, dtd_validation=True, load_dtd=True)

def _subelem(elem, sub_elem_names):
    """
    Return the subelement values of the given element.
    """
    return [elem.find(sub).text if elem.find(sub
            ) is not None else '' for sub in sub_elem_names]

def publicationTo(csv_name):
    """
    INCLUDE:
        article|book|incollection|inproceedings
    CSV ROW ITEMS:
        id(attrib)|title|year(discard row if is not integer)|pages
    """
    INCLUDE = set(['article', 'book', 'incollection', 'inproceedings'])
    ITEMS = ['title', 'year', 'pages']
    emit_log("PROCESS: Start parsing for publication. ")
    f = open(csv_name, 'w', newline='', encoding='utf8')
    writer = csv.writer(f, delimiter=',')
    for _, elem in _context():
        if elem.tag in INCLUDE:
            try:
                year = int(elem.find('year').text)
            except: # year field is not integer or is empty
                continue
            items = [elem.attrib['key']] + _subelem(elem, ITEMS)
            writer.writerow(items)
        elif elem.tag not in ALL_ELEM:
            continue
        _clear_element(elem)
    f.close()
    emit_log("FINISH: Publication generated to " + csv_name)

def articleTo(csv_name):
    """
    ELEMENT TAG:
        article
    CSV ROW ITEMS:
        id(attrib)|journal|volume|number
    """
    ITEMS = ['journal', 'volume', 'number']
    emit_log("PROCESS: Start parsing for article. ")
    f = open(csv_name, 'w', newline='', encoding='utf8')
    writer = csv.writer(f, delimiter=',')
    for _, elem in _context():
        if elem.tag == 'article':
            items = [elem.attrib['key']] + _subelem(elem, ITEMS)
            writer.writerow(items)
        elif elem.tag not in ALL_ELEM:
            continue
        _clear_element(elem)
    f.close()
    emit_log("FINISH: Article generated to " + csv_name)

def inproceedingsTo(csv_name):
    """
    ELEMENT TAG:
        inproceedings
    CSV ROW ITEMS:
        id(attrib)|booktitle
    """
    ITEMS = ['booktitle']
    emit_log("PROCESS: Start parsing for inproceedings. ")
    f = open(csv_name, 'w', newline='', encoding='utf8')
    writer = csv.writer(f, delimiter=',')
    for _, elem in _context():
        if elem.tag == 'inproceedings':
            items = [elem.attrib['key']] + _subelem(elem, ITEMS)
            writer.writerow(items)
        elif elem.tag not in ALL_ELEM:
            continue
        _clear_element(elem)
    f.close()
    emit_log("FINISH: Inproceedings generated to " + csv_name)

def bookTo(csv_name):
    """
    ELEMENT TAG:
        book
    CSV ROW ITEMS:
        id(attrib)|publisher|isbn
    """
    ITEMS = ['publisher', 'isbn']
    emit_log("PROCESS: Start parsing for book. ")
    f = open(csv_name, 'w', newline='', encoding='utf8')
    writer = csv.writer(f, delimiter=',')
    for _, elem in _context():
        if elem.tag == 'book':
            items = [elem.attrib['key']] + _subelem(elem, ITEMS)
            writer.writerow(items)
        elif elem.tag not in ALL_ELEM:
            continue
        _clear_element(elem)
    f.close()
    emit_log("FINISH: Book generated to " + csv_name)

def incollectionTo(csv_name):
    """
    ELEMENT TAG:
        incollection
    CSV ROW ITEMS:
        id(attrib)|crossref
    """
    ITEMS = ['crossref']
    emit_log("PROCESS: Start parsing for incollection. ")
    f = open(csv_name, 'w', newline='', encoding='utf8')
    writer = csv.writer(f, delimiter=',')
    for _, elem in _context():
        if elem.tag == 'incollection':
            items = [elem.attrib['key']] + _subelem(elem, ITEMS)
            writer.writerow(items)
        elif elem.tag not in ALL_ELEM:
            continue
        _clear_element(elem)
    f.close()
    emit_log("FINISH: Incollection generated to " + csv_name)

def authorTo(csv_name):
    """
    INCLUDE:
        article|book|incollection|inproceedings
    CSV ROW ITEM:
        author(no repeat)
    """
    INCLUDE = set(['article', 'book', 'incollection', 'inproceedings'])
    authors = set()
    emit_log("PROCESS: Start parsing for author. ")
    f = open(csv_name, 'w', newline='', encoding='utf8')
    writer = csv.writer(f, delimiter=',')
    for _, elem in _context():
        if elem.tag in INCLUDE:
            authors.update(a.text for a in elem.findall('author'))
        elif elem.tag not in ALL_ELEM:
            continue
        _clear_element(elem)
    writer.writerows([a] for a in sorted(authors))
    f.close()
    emit_log("FINISH: Author generated to " + csv_name)

def authoredTo(csv_name):
    """
    INCLUDE:
        article|book|incollection|inproceedings
    CSV ROW ITEMS:
        id|author(a row for each author)
    """
    INCLUDE = set(['article', 'book', 'incollection', 'inproceedings'])
    emit_log("PROCESS: Start parsing for authored. ")
    f = open(csv_name, 'w', newline='', encoding='utf8')
    writer = csv.writer(f, delimiter=',')
    for _, elem in _context():
        if elem.tag in INCLUDE:
            for a in elem.findall('author'):
                writer.writerow([elem.attrib['key'], a.text])
        elif elem.tag not in ALL_ELEM:
            continue
        _clear_element(elem)
    f.close()
    emit_log("FINISH: Author generated to " + csv_name)


if __name__ == '__main__':
    try:
        _context()
        emit_log("LOG: Successfully loaded " + XML_FILE_PATH)
    except:
        emit_log("ERROR: Failed to load file " + XML_FILE_PATH)
        emit_log("TIP: Check your XML and DTD files. ")
        exit()
    publicationTo("publication.csv")
    articleTo("article.csv")
    inproceedingsTo("inproceedings.csv")
    bookTo("book.csv")
    incollectionTo("incollection.csv")
    authorTo("author.csv")
    authoredTo("authored.csv")
    emit_log("LOG: All tasks finished. ")
