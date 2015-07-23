# Download visa information and make a table

from BeautifulSoup import BeautifulSoup
import urllib2
import json
import pickle
import os

def download_site(site):
    page = urllib2.urlopen(site)
    soup = BeautifulSoup (page)
    tables = soup.findAll("table")
    assert tables is not None
    target_table = None
    for table in tables:
        assert table is not None
        if "wikitable" in table.get("class"):
            target_table = table
            break
    assert target_table is not None
    return target_table

def parse_table (table):
    """Returns mapping from country to status"""
    d = {}
    for row in table.findAll("tr"):
        cols = row.findAll("td")
        if len(cols) >= 3:
            country = cols[0].find("a").text.strip()
            visa_req = cols[1].text.strip()
            if "[" in visa_req:
                visa_req = visa_req.split("[")[0]
            notes = cols[2].text
            d[country] = visa_req
    return d

def parse_demonym_table (table):
    d = {}
    for row in table.findAll("tr"):
        cols = row.findAll("td")
        assert cols is not None
        if len(cols) >= 3:
            assert (all([col is not None for col in cols]))
            country = cols[0].find("a").text.strip()
            adjectival = cols[1].text.strip()
            if "," in adjectival:
                adjectival = adjectival.split(",")[0]
            demonym = cols[2].text
            d[country] = adjectival
    return d

def get_visa_data (citizen_demonym):
    fname = "data/%s.data" % citizen_demonym
    if os.path.exists(fname):
        with open(fname) as fp:
            d = pickle.load(fp)
    else:
        site = "https://en.wikipedia.org/wiki/Visa_requirements_for_%s_citizens" % citizen_demonym
        table = download_site(site)
        assert table is not None
        d = parse_table(table)
    if not os.path.exists(fname):
        with open(fname, "w") as fp:
            pickle.dump(d, fp)
    return d

def print_table (citizen_demonym):
    d = get_visa_data (citizen_demonym)
    categories = set(d.values())
    print "# %s PASSPORT" % citizen_demonym
    for category in categories:
        print "***************** %s ****************" % category
        c_list = [ k for (k, v) in d.iteritems() if v == category]
        print c_list
        print ""

def read_demonyms ():
    """Read demonyms from wikipidea page for all countries and save"""
    fname = "data/demonyms.data"
    if os.path.exists(fname):
        with open(fname) as fp:
            d = pickle.load(fp)
    else:
        site = "https://en.wikipedia.org/wiki/List_of_adjectival_and_demonymic_forms_for_countries_and_nations"
        table = download_site(site)
        d = parse_demonym_table(table)
    if not os.path.exists(fname):
        with open(fname, "w") as fp:
            pickle.dump(d, fp)
    return d

def download_visa_info (start=None):
    d = read_demonyms()
    d_list = d.values()
    d_list.sort()
    if start is not None:
        idx = d_list.index(start)
        d_list = d_list[idx:]
    for demonym in d_list:
        print demonym
        try:
            get_visa_data(demonym.replace(" ", "_"))
        except urllib2.HTTPError as e:
            print e
        except AssertionError as e:
            print e
        except UnicodeEncodeError as e:
            print e

def parse_to_json (pickle_fname, json_fname=None):
    with open(pickle_fname) as fp:
        data = pickle.load(fp)

    if json_fname is None:
        json_fname = pickle_fname.replace(".data", ".json")
    with open(json_fname, "w") as fp:
        json.dump(data, fp)

if __name__ == "__main__":
    #download_visa_info("Russian")
    d = read_demonyms()
    data = {}
    print d
    for country, demonym in d.iteritems():
        fname = "data/%s.data" % demonym.replace(" ", "_")
        if os.path.exists(fname):
            data[country] = demonym
            parse_to_json(fname, fname.replace("data", "json"))
        else:
            #print demonym
            pass
    print json.dumps(data, indent=4)
    with open("json/countries.json", "w") as fp:
        json.dump(data, fp)
