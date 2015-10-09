"""
Dependencies:
- Python 3.4+
- lxml 3.4.4
"""

__version__ = "1.1"

from datetime import datetime
import csv
import re

from lxml import etree

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

def _count(pages):
    """
    Parse pages string and count number of pages.
    There might be multiple pages sepearted by commas.
    VALID FORMATS:
        51         ->Single number
        23-43      ->Range by two numbers
    NON-DIGITS ARE ALLOWED BUT IGNORED:
        AG83-AG120
        90210H     ->Containing alphabets
        8e:1-8e:4
        11:12-21   ->Containing colons
        P1.35      ->Containing dots
        S2/109     ->Containing slashs
        2-3&4      ->Containing ampersands and more...
    INVALID FORMATS:
        I-XXI      ->Roman numerals are not recognized
        0-         ->Incomplete range
        91A-91A-3  ->More than one dash
        f          ->No digits
    ALGORITHM:
        1) Split the string by comma evaluated each part with (2).
        2) Split the part to subparts by dash. If more than two subparts,
           evaluate to zero. If have two subparts, evaluate by (3). If have one
           subpart, evaluate by (4).
        3) For both subparts, convert to number by (4). If not sucessful in
           either subpart, return zero. Subtract first to second, if negative,
           return zero; else return (second - first + 1) as page count.
        4) Search for number consisits of digits. Only take the last one
           (P17.23 -> 23). Return page count as 1 for (2) if find; 0 for (2) if
           not find. Return the number for (3) if find; -1 for (3) if not find.
    """
    cnt = 0
    reRange = r"([\w\d:]+)-([\w\d:]+)"
    for part in re.compile(r",").split(pages):
        subparts = re.compile(r"-").split(part)
        if len(subparts) > 2:
            continue
        else:
            try:
                reDigits = re.compile(r"[\d]+")
                subparts = [int(reDigits.findall(sub)[-1]) for sub in subparts]
            except IndexError:
                continue
            cnt += 1 if len(subparts) == 1 else subparts[1]-subparts[0]+1
    return "" if cnt == 0 else str(cnt)

def publicationTo(csv_name):
    """
    INCLUDE:
        article|book|incollection|inproceedings
    CSV ROW ITEMS:
        id(attrib)|title|year(discard row if is not integer)|pages|count
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
            # count pages
            items += [_count(items[-1])]
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
    #articleTo("article.csv")
    #inproceedingsTo("inproceedings.csv")
    #bookTo("book.csv")
    #incollectionTo("incollection.csv")
    #authorTo("author.csv")
    #authoredTo("authored.csv")
    emit_log("LOG: All tasks finished. ")
