#Download visa information and make a table

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
        if table.get("class") is None:
            continue
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
            if cols[0].find("a"):
                country = cols[0].find("a").text.strip()
            else:
                country = cols[0].text.strip()
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
        if len(cols) >= 2:
            assert (all([col is not None for col in cols]))
            country = cols[0].find("a").text.strip()
            adjectival = cols[1].text.strip()
            if "[" in adjectival:
                adjectival = adjectival.split("[")[0]
            if "," in adjectival:
                # it's a list
                adjectival = adjectival.split(",")
            d[country] = adjectival
    return d

def get_visa_data (citizen_demonym):
    """Given a demonym, fetch information on it. Save it in its own pickle file."""
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

def read_demonyms (cache=True):
    """Read demonyms from wikipidea page for all countries and save"""
    fname = "data/demonyms.data"
    if os.path.exists(fname) and cache:
        with open(fname) as fp:
            d = pickle.load(fp)
    else:
        site = "https://en.wikipedia.org/wiki/List_of_adjectival_and_demonymic_forms_for_countries_and_nations"
        print "[+] downloading demonyms"
        table = download_site(site)
        d = parse_demonym_table(table)
    with open(fname, "w") as fp:
        pickle.dump(d, fp)
    return d

def reverse_dict (d):
    r = {}
    for k, v in d.iteritems():
        r[v] = k

def download_visa_info (start=None):
    d = read_demonyms()
    d_list = d.values()
    d_list.sort()
    if start is not None:
        idx = d_list.index(start)
        d_list = d_list[idx:]
    success_countries = []
    for demonym in d_list:
        if type(demonym) == list:
            for item in demonym:
                print "[+] %s" % item
                try:
                    get_visa_data(item.replace(" ", "_"))
                except urllib2.HTTPError as e:
                    print e
                except AssertionError as e:
                    print e
                except UnicodeEncodeError as e:
                    print e
                else:
                    success_countries.append(item)
                    break
        else:
            print "[+] %s" % demonym
            try:
                get_visa_data(demonym.replace(" ", "_"))
            except urllib2.HTTPError as e:
                print e
            except AssertionError as e:
                print e
            except UnicodeEncodeError as e:
                print e
            else:
                success_countries.append(demonym)
    return success_countries

def pickle_to_json (pickle_fname, json_fname=None):
    with open(pickle_fname) as fp:
        data = pickle.load(fp)

    if json_fname is None:
        json_fname = pickle_fname.replace(".data", ".json")
    with open(json_fname, "w") as fp:
        # human-readable
        json.dump(data, fp, indent=4)

def get_coverage(denom):
    try:
        visa_info = get_visa_data(denom)
    except urllib2.HTTPError as e:
        print denom
        print e
        return None
    except AssertionError as e:
        print denom
        print e
        return None
    except UnicodeEncodeError as e:
        print denom
        print e
        return None
    except TypeError as e:
        print denom
        print e
        return None
    except AttributeError as e:
        print denom
        print e
        return None
    coverage = set([])
    for other_country, status in visa_info.iteritems():
        if "Visa free" in status or "Visa not required" in status:
            coverage.add(other_country)
    return coverage

def count_coverage (denom1, denom2):
    cover1 = get_coverage(denom1)
    cover2 = get_coverage(denom2)
    joint = cover1.union(cover2)
    return len(joint), joint

def get_list_of_countries():
    countries = read_countries()
    for country, demonym in countries:
        get_visa_data_from_json(demonym)

def save_countries (countries):
    with open("json/countries.json", "w") as fp:
        # human-readable
        json.dump(countries, fp, indent=4)

def reformat_json (fname):
    with open(fname) as fp:
        data = json.load(fp)
    with open(fname, "w") as fp:
        json.dump(data, fp, indent=4)

if __name__ == "__main__":
    #d = read_demonyms(cache=False)
    #get_visa_data("South Korean")
    #l = download_visa_info()
    #print l
    #countries = {}
    #for item in l:
        #for k, v in d.iteritems():
             ##abuse of in -> works on strings and lists
            #if item in v:
                #countries[k] = item
    #print countries
    #save_countries(countries)
    #fname = "data/South_Korean.data"
    #pickle_to_json(fname, fname.replace("data", "json"))
    for fname in os.listdir("json"):
        reformat_json("json/" + fname)
