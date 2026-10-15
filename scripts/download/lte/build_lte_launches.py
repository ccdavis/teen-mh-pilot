"""Build lte_launches_long.csv and lte_onset_by_cbsa.csv from the transcribed waves.

Run:  uv run --with xlrd python scripts/build_lte_launches.py
"""
import re
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).parent))
from lte_waves_raw import WAVES  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LTE = ROOT / "data" / "external" / "lte"
BIG4 = ["Verizon", "AT&T", "Sprint", "T-Mobile"]

# ----------------------------------------------------------------------------- CBSA reference
l1 = pd.read_excel(LTE / "list1_2013.xls", skiprows=2, dtype=str).dropna(subset=["CBSA Code", "CBSA Title"])
l2 = pd.read_excel(LTE / "list2_2013.xls", skiprows=2, dtype=str).dropna(subset=["CBSA Code", "CBSA Title", "Principal City Name"])
cbsa = l1.drop_duplicates("CBSA Code")[["CBSA Code", "CBSA Title", "Metropolitan/Micropolitan Statistical Area"]]
cbsa = cbsa.rename(columns={"CBSA Code": "cbsa_code", "CBSA Title": "cbsa_name",
                            "Metropolitan/Micropolitan Statistical Area": "type"})
cbsa_name = dict(zip(cbsa.cbsa_code, cbsa.cbsa_name))
cbsa_type = dict(zip(cbsa.cbsa_code, cbsa.type))


def norm(s):
    s = s.lower().replace("st.", "saint").replace("ft.", "fort").replace("mt.", "mount")
    s = s.replace("'", "").replace("’", "")
    return re.sub(r"[^a-z]", "", s)


# index: (norm city, state) -> [cbsa codes]; from principal cities (list2) and title cities (list1)
idx = {}


def add(city, st, code):
    idx.setdefault((norm(city), st), [])
    if code not in idx[(norm(city), st)]:
        idx[(norm(city), st)].append(code)


for _, r in l2.iterrows():
    title = r["CBSA Title"]
    sts = title.split(",")[-1].strip().split("-")
    for st in sts:
        add(r["Principal City Name"], st, r["CBSA Code"])
for _, r in cbsa.iterrows():
    title = r["cbsa_name"]
    cities = title.split(",")[0].split("-")
    sts = title.split(",")[-1].strip().split("-")
    for c in cities:
        for st in sts:
            add(c, st, r["cbsa_code"])

title2code = {v: k for k, v in cbsa_name.items()}


def T(title):
    return title2code[title]


# Manual mappings whose CBSA title intentionally shares no name token with the market string
# (suburb / county / nickname mapped to its parent CBSA).
INTENTIONAL = {
    "Dallas-Ft. Worth Metroplex, TX", "Fort Worth, TX", "Ft. Lauderdale, FL", "Fort Lauderdale, FL",
    "Fort Lauderdale/Pompano Beach/Deerfield Beach, FL", "West Palm Beach, FL", "Twin Cities, MN",
    "New York City metro area, NY", "Northern New Jersey, NJ", "Bronx/Brooklyn, NY", "Orange County, NY",
    "Oakland, CA", "Oakland/Fremont/Hayward, CA", "Contra Costa County, CA", "Seattle/Tacoma, WA", "Tacoma, WA",
    "North Montgomery County, MD", "Frederick, MD", "Anne Arundel County, MD", "Columbia/Ellicott City, MD",
    "Santa Ana/Anaheim, CA", "Greater Lehigh Valley, PA", "Greater Fairfield, CT", "Fairfield County, CT",
    "Greater Hampton Roads, VA", "Norfolk/Virginia Beach/Portsmouth, VA", "Norfolk/Virginia Beach/Newport News, VA",
    "Quad Cities, IA", "Tri-Cities, TN", "Chapel Hill, NC", "Hopkinsville, KY", "Kahului-Wailuku, HI", "Lahaina, HI",
    "Kauai, HI", "Lihue, HI", "Honolulu, HI", "Hyannis/Mid-Cape, MA", "Cape Cod, MA", "Martha's Vineyard, MA",
    "Peabody, MA", "Fitchburg/Leominster, MA", "Manchester/Nashua, NH", "Portsmouth, NH", "Poughkeepsie, NY",
    "Cattaraugus/Allegany, NY", "Saratoga Springs, NY", "Sharon/Farrell/Hermitage, PA", "Northern Cambria County, PA",
    "Mechanicsburg, PA", "Juniata and Mifflin counties, PA", "Franklin County, PA", "Martinsburg, WV",
    "Jefferson County, WV", "Clarke County, VA", "Fredericksburg, VA", "Huntington, WV", "Oak Hill, WV",
    "Bay Minette, AL", "Picayune, MS", "Fort Polk South, LA", "Granbury-Hood County, TX", "Anderson, IN",
    "Downriver Wayne and Monroe Counties, MI", "Holland, MI", "Allegan, MI", "Mayer, AZ", "Sedona, AZ",
    "Cottonwood, AZ", "Saddlebrook, AZ", "Silverthorne, CO", "Salinas/Monterey/Seaside, CA",
    "Salinas-Seaside-Monterey, CA", "Kingsport, TN", "Palm Bay, FL", "Port St. Lucie, FL", "Palm Coast, FL",
    "White River Junction, VT", "Punxsutawney/DuBois/Clearfield, PA", "Waterville/Augusta, ME", "Gary, IN",
    "Dunn, NC", "Salisbury, NC", "Statesville, NC", "Lincolnton, NC", "Warner Robins, GA", "Newnan, GA",
    "Carrollton, GA", "Ponce, PR", "Mayaguez, PR", "Prewitt, NM", "La Salle/Peru/Ottawa, IL", "Prescott/Prescott Valley, AZ",
    "Port Townsend, WA", "Port Angeles/Sequim, WA", "Kennewick/Pasco/Richland, WA", "Fort Collins-Loveland, CO",
    "Killeen-Temple, TX", "Temple-Killeen, TX", "Temple, TX", "Greenwood-Cleveland, MS", "Lake City, FL",
    "Marshfield/Wisconsin Rapids, WI", "Whitewater, WI", "Fort Atkinson, WI", "Vicksburg, MS", "Findlay/Tiffin, OH",
}

# manual overrides: exact market string -> list of cbsa codes (2013 delineations)
MANUAL = {
    "Dallas-Ft. Worth Metroplex, TX": ["19100"], "Dallas-Fort Worth, TX": ["19100"], "Dallas, TX": ["19100"],
    "Fort Worth, TX": ["19100"], "Ft. Lauderdale, FL": ["33100"], "Fort Lauderdale, FL": ["33100"],
    "Fort Lauderdale/Pompano Beach/Deerfield Beach, FL": ["33100"], "Miami, FL": ["33100"],
    "West Palm Beach, FL": ["33100"], "Minneapolis/Saint Paul, MN": ["33460"], "Minneapolis/St. Paul, MN": ["33460"],
    "Minneapolis, MN": ["33460"], "Twin Cities, MN": ["33460"], "New York, NY": ["35620"],
    "New York City metro area, NY": ["35620"], "Northern New Jersey, NJ": ["35620"], "Bronx/Brooklyn, NY": ["35620"],
    "Orange County, NY": ["35620"], "Oakland, CA": ["41860"], "Oakland/Fremont/Hayward, CA": ["41860"],
    "Contra Costa County, CA": ["41860"], "San Francisco, CA": ["41860"], "San Jose, CA": ["41940"],
    "Seattle/Tacoma, WA": ["42660"], "Seattle, WA": ["42660"], "Tacoma, WA": ["42660"], "Washington, DC": ["47900"],
    "North Montgomery County, MD": ["47900"], "Frederick, MD": ["47900"], "Anne Arundel County, MD": ["12580"],
    "Columbia/Ellicott City, MD": ["12580"], "Los Angeles, CA": ["31080"], "Santa Ana/Anaheim, CA": ["31080"],
    "Greater Lehigh Valley, PA": ["10900"], "Greater Fairfield, CT": ["14860"], "Fairfield County, CT": ["14860"],
    "Bridgeport/Stamford/Norwalk, CT": ["14860"], "Bridgeport, CT": ["14860"], "Greater Providence, RI": ["39300"],
    "Providence, RI": ["39300"], "Greater Hampton Roads, VA": ["47260"], "Norfolk/Virginia Beach/Portsmouth, VA": ["47260"],
    "Norfolk/Virginia Beach/Newport News, VA": ["47260"], "Quad Cities, IA": ["19340"], "Tri-Cities, TN": ["28700"],
    "Kingsport, TN": ["28700"], "Raleigh-Durham, NC": ["39580", "20500"], "Raleigh, NC": ["39580"],
    "Chapel Hill, NC": ["20500"], "Durham, NC": ["20500"], "Greensboro/Winston-Salem/High Point, NC": ["24660", "49180"],
    "Fayetteville-Lumberton, NC": ["22180", "31300"], "Lumberton, NC": ["31300"], "Salt Lake City-Ogden, UT": ["41620", "36260"],
    "Provo, UT": ["39340"], "Provo-Orem, UT": ["39340"], "Ogden, UT": ["36260"], "Omaha/Council Bluffs, NE": ["36540"],
    "Omaha, NE": ["36540"], "Kansas City, MO": ["28140"], "Kansas City, KS": ["28140"], "St. Louis, MO": ["41180"],
    "Springfield/Branson, MO": ["44180", "14700"], "Wilkes Barre/Scranton, PA": ["42540"], "Hilo, HI": ["25900"],
    "Honolulu, HI": ["46520"], "Kahului-Wailuku, HI": ["27980"], "Lahaina, HI": ["27980"], "Kauai, HI": ["28180"],
    "Lihue, HI": ["27980"], "Clarksville, TN": ["17300"], "Hopkinsville, KY": ["17300"], "Cleveland, TN": ["17420"],
    "Temple-Killeen, TX": ["28660"], "Killeen-Temple, TX": ["28660"], "Temple, TX": ["28660"],
    "Bryan-College Station, TX": ["17780"], "Greenville-Spartanburg, SC": ["24860", "43900"],
    "Greenville/Mauldin/Easley, SC": ["24860"], "Salinas/Monterey/Seaside, CA": ["41500"],
    "Salinas-Seaside-Monterey, CA": ["41500"], "Salinas, CA": ["41500"], "Fayetteville/Springdale/Rogers, AR": ["22220"],
    "Champaign/Urbana, IL": ["16580"], "Beaumont/Port Arthur, TX": ["13140"], "Daytona, FL": ["19660"],
    "Daytona Beach, FL": ["19660"], "Sarasota-Bradenton, FL": ["35840"], "Lakeland, FL": ["29460"],
    "Lakeland/Winter Haven, FL": ["29460"], "Tampa-St. Petersburg, FL": ["45300"], "Tampa, FL": ["45300"],
    "Melbourne/Titusville, FL": ["37340"], "Melbourne, FL": ["37340"], "Palm Bay, FL": ["37340"],
    "Fort Pierce/Vero Beach, FL": ["38940", "42680"], "Fort Pierce, FL": ["38940"], "Port St. Lucie, FL": ["38940"],
    "Cape Coral/Fort Myers, FL": ["15980"], "Port Charlotte/Punta Gorda, FL": ["39460"], "Naples, FL": ["34940"],
    "Key West, FL": ["28580"], "Fort Walton Beach, FL": ["18880"], "Homosassa Springs, FL": ["26140"],
    "Sebring, FL": ["42700"], "Palatka, FL": ["37260"], "Palm Coast, FL": ["19660"], "Lake City, FL": ["29380"],
    "Youngstown/Warren, OH": ["49660"], "Findlay/Tiffin, OH": ["22300", "45780"], "Manchester/Nashua, NH": ["31700"],
    "Fitchburg/Leominster, MA": ["49340"], "Hyannis/Mid-Cape, MA": ["12700"], "Cape Cod, MA": ["12700"],
    "Martha's Vineyard, MA": ["47240"], "Peabody, MA": ["14460"], "Worcester, MA": ["49340"],
    "Springfield, MA": ["44140"], "Boston, MA": ["14460"], "Greater Portland, ME": ["38860"], "Portland, ME": ["38860"],
    "Waterville/Augusta, ME": ["12300"], "Lewiston-Auburn, ME": ["30340"],
    "Burlington, VT": ["15540"], "Rutland, VT": ["40860"], "Bennington, VT": ["13540"], "Brattleboro, VT": ["14380"],
    "White River Junction, VT": [T("Claremont-Lebanon, NH-VT")], "New London County, CT": ["35980"], "Atlantic City/Toms River, NJ": ["12100"],
    "Atlantic City, NJ": ["12100"], "Poughkeepsie, NY": ["35620"], "Glens Falls, NY": ["24020"],
    "Cattaraugus/Allegany, NY": ["36460"], "Elmira/Corning/Hornell, NY": ["21300", "18500"],
    "Saratoga Springs, NY": ["10580"], "Albany, NY": ["10580"], "Utica-Rome, NY": ["46540"], "Batavia, NY": ["12860"],
    "Jamestown, NY": ["27460"], "Oneonta, NY": ["36580"], "Punxsutawney/DuBois/Clearfield, PA": ["20180"],
    "Sharon/Farrell/Hermitage, PA": ["49660"], "Oil City/Franklin, PA": ["36020"], "Northern Cambria County, PA": ["27780"],
    "Indiana, PA": ["26860"], "Harrisburg/Carlisle/Hershey, PA": ["25420"], "Mechanicsburg, PA": ["25420"],
    "Harrisburg, PA": ["25420"], "Juniata and Mifflin counties, PA": ["30380"], "State College, PA": ["44300"],
    "Lebanon, PA": ["30140"], "Franklin County, PA": ["16540"], "York/Hanover, PA": ["49620"],
    "Hagerstown, MD": ["25180"], "Martinsburg, WV": ["25180"], "Jefferson County, WV": ["47900"],
    "Clarke County, VA": ["47900"], "Winchester, VA": ["49020"], "Shenandoah County, VA": [],
    "Staunton/Waynesboro, VA": ["44420"], "Charlottesville, VA": ["16820"], "Fredericksburg, VA": ["47900"],
    "Ashland, KY": ["26580"], "Huntington, WV": ["26580"], "Logan, WV": [], "Beckley, WV": ["13220"],
    "Oak Hill, WV": ["13220"], "Clarksburg, WV": ["17220"], "Morgantown, WV": ["34060"],
    "Greater Mobile, AL": ["33660"], "Mobile, AL": ["33660"], "Bay Minette, AL": ["19300"],
    "Biloxi/Gulfport/Pascagoula, MS": ["25060"], "Gulfport, MS": ["25060"], "Picayune, MS": [T("Picayune, MS")],
    "Greenville/Greenwood, MS": ["24740", "24980"], "Greenwood-Cleveland, MS": ["24980", "17380"],
    "Tunica, MS": ["32820"], "Corinth, MS": ["18420"], "Oxford, MS": ["37060"], "West Point, MS": [],
    "Laurel, MS": ["29860"], "Natchez, MS": ["35020"], "Brookhaven, MS": ["15020"], "McComb, MS": ["32620"],
    "Houma/Thibodaux, LA": ["26380"], "Houma/Bayou Cane/Thibodaux, LA": ["26380"], "Lafayette/New Iberia, LA": ["29180"],
    "New Iberia, LA": ["29180"], "Morgan City, LA": ["34020"], "Fort Polk South, LA": ["22860"], "Ruston, LA": ["40820"],
    "El Dorado/Magnolia, AR": ["20980", "31620"], "Sherman/Denison, TX": ["43300"], "Sherman-Denison, TX": ["43300"],
    "Denison, TX": ["43300"], "Lufkin/Nacogdoches, TX": ["31260", "34860"], "Nacogdoches-Lufkin, TX": ["34860", "31260"],
    "Brownsville, TX": ["15180"], "Brownsville/Harlingen, TX": ["15180"], "McAllen, TX": ["32580"],
    "McAllen/Edinburg/Mission, TX": ["32580"], "Granbury-Hood County, TX": ["19100"], "Big Spring, TX": ["13700"],
    "Manhattan/Junction City, KS": ["31740"], "Kokomo/Logansport, IN": ["29020", "30900"],
    "Michigan City/La Porte, IN": ["33140"], "Elkhart/Goshen, IN": ["21140"], "Indianapolis/Carmel, IN": ["26900"],
    "South Bend/Mishawaka, IN": ["43780"], "West Lafayette, IN": ["29200"], "Lafayette, IN": ["29200"],
    "Anderson, IN": ["26900"], "Downriver Wayne and Monroe Counties, MI": ["19820", "33780"],
    "Benton Harbor/St. Joseph, MI": ["35660"], "St. Joseph/Benton Harbor, MI": ["35660"],
    "Lansing/East Lansing, MI": ["29620"], "Houghton, MI": ["26820"], "Holland, MI": ["26090"], "Allegan, MI": ["26090"],
    "Adrian, MI": ["10300"], "Bozeman/Livingston, MT": ["14580"], "Fergus Falls/Alexandria, MN": ["10820"],
    "Mankato/North Mankato, MN": ["31860"], "Faribault/Northfield, MN": ["22060"], "Grand Rapids, MN": [],
    "Decatur/Effingham, IL": ["19500", "20820"], "Kankakee/Bradley-Bourbonnais, IL": ["28100"],
    "Kankakee-Bradley, IL": ["28100"], "La Salle/Peru/Ottawa, IL": [T("Ottawa-Peru, IL")], "Carbondale, IL": ["16060"],
    "Mount Vernon, IL": ["34500"], "Rochelle, IL": ["40300"], "Mason City/Charles City, IA": ["32380"],
    "Lake of the Ozarks, MO": [], "Lake Charles, LA": ["29340"], "Jefferson City, MO": ["27620"],
    "Salem/Albany/Corvallis, OR": ["41420", "10540", "18700"], "Albany/Corvallis, OR": ["10540", "18700"],
    "Medford/Grants Pass, OR": ["32780", "24420"], "Medford-Ashland, OR": ["32780"], "Roseburg/Sutherlin, OR": ["40700"],
    "Eugene/Springfield, OR": ["21660"], "Chico/Oroville, CA": ["17020"], "Chico-Oroville, CA": ["17020"],
    "Yuba City/Marysville, CA": ["49700"], "Visalia/Porterville, CA": ["47300"], "Stockton-Lodi, CA": ["44700"],
    "Santa Rosa/Petaluma, CA": ["42220"], "Vallejo/Fairfield, CA": ["46700"], "Red Bluff, CA": ["39780"],
    "Kennewick/Pasco/Richland, WA": ["28420"], "Port Angeles/Sequim, WA": ["38820"], "Port Townsend, WA": ["38820"],
    "Flagstaff/Williams, AZ": ["22380"], "Prescott/Prescott Valley, AZ": [T("Prescott, AZ")], "Casa Grande, AZ": ["38060"],
    "Saddlebrook, AZ": ["46060"], "Payson, AZ": ["37740"], "Mayer, AZ": [T("Prescott, AZ")], "Sedona, AZ": [T("Prescott, AZ")],
    "Cottonwood, AZ": [T("Prescott, AZ")], "Prewitt, NM": ["23700"], "Silverthorne, CO": ["14720"], "Durango, CO": ["20420"],
    "Fort Collins-Loveland, CO": ["22660"], "Boulder, CO": ["14500"], "Coeur d'Alene, ID": ["17660"],
    "Burley, ID": ["15420"], "Blackfoot, ID": ["14540"], "Lewiston, ID": ["30300"], "St. Thomas, VI": [],
    "St. Croix, VI": [], "San Juan, PR": ["41980"], "Ponce, PR": ["38660"], "Mayaguez, PR": ["32420"],
    "Starkville, MS": ["44260"], "Dyersburg, TN": ["20540"], "Martin, TN": ["32280"], "Greeneville, TN": ["24620"],
    "Tullahoma, TN": ["46100"], "Cookeville, TN": ["18260"], "Auburn/Opelika, AL": ["12220"], "Anniston/Oxford, AL": ["11500"],
    "Warsaw, IN": ["48700"], "Kerrville, TX": ["28500"], "Eagle Pass, TX": ["20580"], "Del Rio, TX": ["19620"],
    "Jacksonville, TX": ["27380"], "Athens, TX": ["11380"], "Corsicana, TX": ["18620"], "Paris, TX": ["37580"],
    "Huntsville, TX": ["26660"], "Marshall, TX": ["30980"], "Longview, TX": ["30980"], "Texarkana, TX": ["45500"],
    "Mt. Sterling, KY": ["34460"], "Elizabethtown, KY": ["21060"], "Frankfort, KY": ["23180"], "Paducah, KY": ["37140"],
    "Bowling Green, KY": ["14540"], "Owensboro, KY": ["36980"], "Twin Falls, ID": ["46300"],
    "Tifton, GA": ["45620"], "Waycross, GA": ["48180"], "Milledgeville, GA": ["33300"], "Macon/Warner Robins, GA": ["31420", "47580"],
    "Warner Robins, GA": ["47580"], "Calhoun, GA": ["15660"], "Carrollton, GA": ["12060"], "Newnan, GA": ["12060"],
    "Gainesville, GA": ["23580"], "LaGrange, GA": ["29300"], "Dalton, GA": ["19140"], "Rome, GA": ["40660"],
    "Brunswick, GA": ["15260"], "Rock Springs, WY": ["40540"], "Laramie, WY": ["29660"], "Gillette, WY": ["24220"],
    "Sheridan, WY": ["43260"], "Grand Junction, CO": ["24300"], "Butte, MT": ["15580"], "Pierre, SD": ["38180"],
    "Mitchell, SD": ["33580"], "Dickinson, ND": ["19860"], "Williston, ND": ["48780"], "Minot, ND": ["33500"],
    "Hays, KS": ["25700"], "Great Bend, KS": ["24460"], "Parsons, KS": ["37660"], "McPherson, KS": ["32700"],
    "Dodge City, KS": ["19980"], "Garden City, KS": ["23780"], "Worthington, MN": ["49380"], "Brainerd, MN": ["14660"],
    "Marquette, MI": ["31940"], "Traverse City, MI": ["45900"], "Muskegon, MI": ["34740"], "Battle Creek, MI": ["12980"],
    "Norfolk, NE": ["35740"], "North Platte, NE": ["35820"], "McCook, NE": ["32740"], "Hastings, NE": ["25580"],
    "Kearney, NE": ["28260"], "Oskaloosa, IA": ["36820"], "Marshalltown, IA": ["31740"], "Farmington, NM": ["22140"],
    "Gallup, NM": ["23700"], "Clovis, NM": ["17580"], "Price, UT": ["39220"], "Richfield, UT": [], "Cedar City, UT": ["16260"],
    "Logan, UT": ["30860"], "Klamath Falls, OR": ["28900"], "Bend, OR": ["13460"], "Longview, WA": ["31020"],
    "Centralia, WA": ["16500"], "Aberdeen, WA": ["10140"], "Walla Walla, WA": ["47460"], "Moses Lake, WA": ["34180"],
    "Bellingham, WA": ["13380"], "Olympia, WA": ["36500"], "Bremerton, WA": ["14740"], "Yakima, WA": ["49420"],
    "Port Angeles, WA": ["38820"], "Redding, CA": ["39820"], "Hot Springs, AR": ["26300"], "Searcy, AR": ["42620"],
    "Harrison, AR": ["25460"], "Russellville, AR": ["40780"], "Van Buren, AR": ["22900"], "Siloam Springs, AR": ["22220"],
    "Mountain Home, AR": ["34260"], "Pine Bluff, AR": ["38220"], "Jonesboro, AR": ["27860"], "Fort Smith, AR": ["22900"],
    "West Plains, MO": ["48460"], "Rolla, MO": ["40620"], "Poplar Bluff, MO": ["38740"], "Kirksville, MO": ["28860"],
    "Farmington, MO": ["22100"], "Cape Girardeau, MO": ["16020"], "Sedalia, MO": ["42740"], "Joplin, MO": ["27900"],
    "Columbia, MO": ["17860"], "Whitewater, WI": ["48020"], "Fort Atkinson, WI": ["48020"], "Baraboo, WI": ["12660"],
    "Beaver Dam, WI": ["13180"], "Marshfield/Wisconsin Rapids, WI": ["48140"], "Stevens Point, WI": ["44620"],
    "Wausau, WI": ["48140"], "Janesville, WI": ["27500"], "Janesville/Beloit, WI": ["27500"], "Manitowoc, WI": ["31820"],
    "Fond du Lac, WI": ["22540"], "Sheboygan, WI": ["43100"], "Appleton/Oshkosh, WI": ["11540", "36780"],
    "Oshkosh-Neenah, WI": ["36780"], "Appleton, WI": ["11540"], "Eau Claire, WI": ["20740"], "La Crosse, WI": ["29100"],
    "Green Bay, WI": ["24580"], "Madison, WI": ["31540"], "Sandusky, OH": ["41780"], "Ashtabula, OH": ["11780"],
    "Bucyrus, OH": ["15340"], "Defiance, OH": ["19580"], "Chillicothe, OH": ["17060"], "Portsmouth, OH": ["39020"],
    "Zanesville, OH": ["49780"], "Lima, OH": ["30620"], "Mansfield, OH": ["31900"], "Canton, OH": ["15940"],
    "Akron, OH": ["10420"], "Dayton, OH": ["19380"], "Toledo, OH": ["45780"], "East Stroudsburg, PA": ["20700"],
    "Pottsville, PA": ["39060"], "Reading, PA": ["39740"], "Lancaster, PA": ["29540"], "York, PA": ["49620"],
    "Somerset, PA": ["43740"], "Bedford, PA": ["13340"], "New Castle, PA": ["35260"], "Meadville, PA": ["32740"],
    "Altoona, PA": ["11020"], "Johnstown, PA": ["27780"], "Erie, PA": ["21500"], "Dover, DE": ["20100"],
    "Salisbury, MD": ["41540"], "Portsmouth, NH": ["14460"], "Utica, NY": ["46540"], "Ithaca, NY": ["27060"],
    "Binghamton, NY": ["13780"], "Hickory/Lenoir, NC": ["25860"], "New Bern, NC": ["35100"], "Goldsboro, NC": ["24140"],
    "Kinston, NC": ["28820"], "Roanoke Rapids, NC": ["40260"], "Rocky Mount, NC": ["40580"], "Wilson, NC": ["48980"],
    "Albemarle, NC": ["10620"], "Lincolnton, NC": ["16740"], "Salisbury, NC": ["40580"], "Shelby, NC": ["43140"],
    "Statesville, NC": ["16740"], "Henderson, NC": ["25780"], "Dunn, NC": ["20500"], "Burlington, NC": ["15500"],
    "Jacksonville, NC": ["27340"], "Greenville, NC": ["24780"], "Fayetteville, NC": ["22180"], "Wilmington, NC": ["48900"],
    "Asheville, NC": ["11700"], "Hilton Head, SC": ["25940"], "Orangeburg, SC": ["36700"], "Myrtle Beach, SC": ["34820"],
    "Anderson, SC": ["24860"], "Greenwood, SC": ["24940"], "Florence, SC": ["22500"], "Dillon, SC": ["20140"],
    "Columbia, SC": ["17900"], "Charleston, SC": ["16700"], "Charleston, WV": ["16620"], "Roanoke, VA": ["40220"],
    "Lynchburg, VA": ["31340"], "Danville, VA": ["19260"], "Martinsville, VA": ["32300"], "Harrisonburg, VA": ["25500"],
    "Richmond, VA": ["40060"], "Decatur, AL": ["19460"], "Florence, AL": ["22520"], "Gadsden, AL": ["23460"],
    "Selma, AL": ["42820"], "Dothan, AL": ["20020"], "Tuscaloosa, AL": ["46220"], "Auburn, AL": ["12220"],
    "Huntsville, AL": ["26620"], "Montgomery, AL": ["33860"], "Birmingham, AL": ["13820"],
    "Alexandria, LA": ["10780"], "Monroe, LA": ["33740"], "Hammond, LA": ["25220"], "Shreveport, LA": ["43340"],
    "Baton Rouge, LA": ["12940"], "New Orleans, LA": ["35380"], "Lafayette, LA": ["29180"],
    "Hattiesburg, MS": ["25620"], "Tupelo, MS": ["46980"], "Jackson, MS": ["27140"], "Vicksburg, MS": ["46980"],
    "Greenville, MS": ["24740"], "Greenwood, MS": ["24980"], "Grenada, MS": ["24900"], "Meridian, MS": ["32940"],
    "Columbus, MS": ["18060"], "Jackson, MI": ["27100"], "Jackson, TN": ["27180"], "Monroe, MI": ["33780"],
    "Bay City, MI": ["13020"], "Saginaw, MI": ["40980"], "Flint, MI": ["22420"], "Kalamazoo, MI": ["28020"],
    "Lansing, MI": ["29620"], "Grand Rapids, MI": ["24340"], "Detroit, MI": ["19820"],
    "Fargo, ND": ["22020"], "Grand Forks, ND": ["24220"], "Bismarck, ND": ["13900"], "Aberdeen, SD": ["10100"],
    "Rapid City, SD": ["39660"], "Sioux Falls, SD": ["43620"], "Sioux City, IA": ["43580"], "Iowa City, IA": ["26980"],
    "Cedar Rapids, IA": ["16300"], "Des Moines, IA": ["19780"], "Lincoln, NE": ["30700"],
    "Topeka, KS": ["45820"], "Wichita, KS": ["48620"], "Salina, KS": ["41460"], "Enid, OK": ["21420"],
    "Ardmore, OK": ["11620"], "Ponca City, OK": ["38620"], "Bartlesville, OK": ["12780"], "Lawton, OK": ["30020"],
    "Stillwater, OK": ["44660"], "Muskogee, OK": ["34780"], "Tulsa, OK": ["46140"], "Oklahoma City, OK": ["36420"],
    "Amarillo, TX": ["11100"], "Abilene, TX": ["10180"], "San Angelo, TX": ["41660"], "Midland, TX": ["33260"],
    "Odessa, TX": ["36220"], "Laredo, TX": ["29700"], "Victoria, TX": ["47020"], "Wichita Falls, TX": ["48660"],
    "Tyler, TX": ["46340"], "Waco, TX": ["47380"], "Corpus Christi, TX": ["18580"], "El Paso, TX": ["21340"],
    "Beaumont, TX": ["13140"], "Austin, TX": ["12420"], "Houston, TX": ["26420"], "San Antonio, TX": ["41700"],
    "Las Cruces, NM": ["29740"], "Santa Fe, NM": ["42140"], "Albuquerque, NM": ["10740"], "Tucson, AZ": ["46060"],
    "Phoenix, AZ": ["38060"], "Las Vegas, NV": ["29820"], "Reno, NV": ["39900"], "Boise, ID": ["14260"],
    "Spokane, WA": ["44060"], "Portland, OR": ["38900"], "Salem, OR": ["41420"], "Corvallis, OR": ["18700"],
    "Eugene, OR": ["21660"], "Anchorage, AK": ["11260"], "Fairbanks, AK": ["21820"], "Pueblo, CO": ["39380"],
    "Colorado Springs, CO": ["17820"], "Fort Collins, CO": ["22660"], "Lamar, CO": [], "La Junta, CO": [],
    "Denver, CO": ["19740"], "Bakersfield, CA": ["12540"], "Fresno, CA": ["23420"], "Sacramento, CA": ["40900"],
    "Modesto, CA": ["33700"], "Stockton, CA": ["44700"], "San Diego, CA": ["41740"], "San Luis Obispo, CA": ["42020"],
    "Santa Barbara, CA": ["42200"], "Napa, CA": ["34900"], "Kalispell, MT": ["28180"], "Missoula, MT": ["33540"],
    "Nashville, TN": ["34980"], "Memphis, TN": ["32820"], "Knoxville, TN": ["28940"], "Chattanooga, TN": ["16860"],
    "Louisville, KY": ["31140"], "Lexington, KY": ["30460"], "Cincinnati, OH": ["17140"], "Columbus, OH": ["18140"],
    "Cleveland, OH": ["17460"], "Pittsburgh, PA": ["38300"], "Philadelphia, PA": ["37980"], "Baltimore, MD": ["12580"],
    "Rochester, NY": ["40380"], "Syracuse, NY": ["45060"], "Buffalo, NY": ["15380"], "Hartford, CT": ["25540"],
    "New Haven, CT": ["35300"], "Chicago, IL": ["16980"], "Rockford, IL": ["40420"], "Peoria, IL": ["37900"],
    "Springfield, IL": ["44100"], "Bloomington, IL": ["14010"], "Decatur, IL": ["19500"], "Danville, IL": ["19180"],
    "Mattoon, IL": ["16660"], "Centralia, IL": ["16460"], "Milwaukee, WI": ["33340"], "Indianapolis, IN": ["26900"],
    "Fort Wayne, IN": ["23060"], "Evansville, IN": ["21780"], "South Bend, IN": ["43780"], "Terre Haute, IN": ["45460"],
    "Elkhart, IN": ["21140"], "Bloomington, IN": ["14020"], "Muncie, IN": ["34620"], "Columbus, IN": ["18020"],
    "Marion, IN": ["31980"], "Kokomo, IN": ["29020"], "Gary, IN": ["16980"], "Columbus, GA": ["17980"],
    "Augusta, GA": ["12260"], "Savannah, GA": ["42340"], "Athens, GA": ["12020"], "Atlanta, GA": ["12060"],
    "Valdosta, GA": ["46660"], "Jacksonville, FL": ["27260"], "Orlando, FL": ["36740"], "Gainesville, FL": ["23540"],
    "Tallahassee, FL": ["45220"], "Pensacola, FL": ["37860"], "Panama City, FL": ["37460"], "Ocala, FL": ["36100"],
    "Charlotte, NC": ["16740"], "Duluth, MN": ["20260"], "St. Cloud, MN": ["41060"], "Rochester, MN": ["40340"],
    "Mankato, MN": ["31860"], "New Ulm, MN": ["35580"], "Little Rock, AR": ["30780"], "Green Bay, WI": ["24580"],
}


def auto_match(market):
    m = re.match(r"^(.*),\s*([A-Z]{2})$", market.strip())
    if not m:
        return []
    names, st = m.group(1), m.group(2)
    for tok in re.split(r"/|-", names):
        tok = re.sub(r"^(Greater|North|Northern|Southern|Central)\s+", "", tok.strip())
        tok = re.sub(r"\s+(County|Counties|area|Area|metro area)$", "", tok)
        hit = idx.get((norm(tok), st))
        if hit:
            return [hit[0]]
    return []


def shares_token(market, code):
    mtoks = {norm(t) for t in re.split(r"/|-|,", market) if t.strip()}
    ctoks = {norm(t) for t in re.split(r"-|,", cbsa_name[code]) if t.strip()}
    return any(a and b and (a in b or b in a) for a in mtoks for b in ctoks)


MANUAL_WARN = []


def match(market):
    auto = auto_match(market)
    if market in MANUAL:
        codes = [c for c in MANUAL[market] if c in cbsa_name]
        ok = market in INTENTIONAL or all(shares_token(market, c) for c in codes)
        if codes and ok:
            return codes
        if not codes and not MANUAL[market]:
            return []  # deliberately unmapped (no CBSA)
        MANUAL_WARN.append((market, MANUAL[market], auto))
    return auto


rows = []
unmatched = []
for w in WAVES:
    for mk in w["markets"]:
        m = re.match(r"^(.*),\s*([A-Z]{2})$", mk.strip())
        st = m.group(2) if m else ""
        codes = match(mk)
        if not codes:
            unmatched.append((w["carrier"], mk))
            codes = [""]
        for c in codes:
            rows.append(dict(carrier=w["carrier"], market_name_as_announced=mk, state=st, launch_date=w["date"],
                             cbsa_code=c, cbsa_name=cbsa_name.get(c, ""), cbsa_type=cbsa_type.get(c, ""),
                             source_url=w["source_url"], source_note=w["source_note"], confidence=w["confidence"]))

long = pd.DataFrame(rows)
long.to_csv(LTE / "lte_launches_long.csv", index=False)
print(f"long rows: {len(long)}; unmatched markets: {len(unmatched)}")
for w_ in MANUAL_WARN:
    print("  MANUAL OVERRIDDEN (name check failed):", w_)
for u in unmatched:
    print("  UNMATCHED:", u)

# ----------------------------------------------------------------------------- population ranks
pop_path = LTE / "cbsa-est2013-alldata.csv"
if not pop_path.exists():
    url = "https://www2.census.gov/programs-surveys/popest/datasets/2010-2013/metro/totals/cbsa-est2013-alldata.csv"
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    pop_path.write_bytes(r.content)
pop = pd.read_csv(pop_path, encoding="latin-1", dtype={"CBSA": str})
pop = pop[(pop["LSAD"] == "Metropolitan Statistical Area")][["CBSA", "NAME", "POPESTIMATE2013"]]
pop = pop.sort_values("POPESTIMATE2013", ascending=False).reset_index(drop=True)
pop["pop_rank_2013"] = pop.index + 1
pop_rank = dict(zip(pop.CBSA, pop.pop_rank_2013))
pop_est = dict(zip(pop.CBSA, pop.POPESTIMATE2013))

# ----------------------------------------------------------------------------- derived per-CBSA onset
CONF_RANK = {"high": 0, "medium": 1, "low": 2}
b4 = long[(long.carrier.isin(BIG4)) & (long.cbsa_code != "")].copy()
b4["date_sort"] = b4.launch_date.str.pad(10, side="right", fillchar="9")  # YYYY-MM sorts after any day in month? no:
# treat month-only dates as the last day of that month for ordering purposes
b4["date_sort"] = b4.launch_date.apply(lambda d: d if len(d) == 10 else d + "-31")
b4["conf_rank"] = b4.confidence.map(CONF_RANK)


def carrier_date(g):
    # earliest date among high/medium rows; fall back to low-confidence rows only if nothing better
    hm = g[g.conf_rank <= 1]
    use = hm if len(hm) else g
    use = use.sort_values("date_sort")
    return use.iloc[0]


out = []
for code, g in b4.groupby("cbsa_code"):
    rec = dict(cbsa_code=code, cbsa_name=cbsa_name[code], cbsa_type=cbsa_type[code],
               pop_2013=pop_est.get(code), pop_rank_2013=pop_rank.get(code))
    cds = {}
    for car, gc in g.groupby("carrier"):
        r = carrier_date(gc)
        cds[car] = (r.date_sort, r.launch_date, r.confidence)
    ordered = sorted(cds.items(), key=lambda kv: kv[1][0])
    rec["first_launch_date"] = ordered[0][1][1]
    rec["first_carrier"] = ordered[0][0]
    rec["first_confidence"] = ordered[0][1][2]
    rec["second_carrier_date"] = ordered[1][1][1] if len(ordered) > 1 else ""
    rec["second_carrier"] = ordered[1][0] if len(ordered) > 1 else ""
    for car, col in [("Verizon", "verizon_date"), ("AT&T", "att_date"), ("Sprint", "sprint_date"), ("T-Mobile", "tmobile_date")]:
        rec[col] = cds[car][1] if car in cds else ""
        rec[col.replace("_date", "_confidence")] = cds[car][2] if car in cds else ""
    rec["n_carriers"] = len(cds)
    rec["n_sources"] = g.source_url.nunique()
    out.append(rec)
onset = pd.DataFrame(out).sort_values(["pop_rank_2013", "cbsa_code"], na_position="last")
onset.to_csv(LTE / "lte_onset_by_cbsa.csv", index=False)

# ----------------------------------------------------------------------------- coverage report
print(f"CBSAs with a first-launch date: {len(onset)} (metro: {(onset.cbsa_type.str.startswith('Metro')).sum()})")
for n in (50, 100, 150):
    top = pop.head(n).CBSA
    have = onset[onset.cbsa_code.isin(top)]
    print(f"top-{n} metros: any-carrier {len(have)}/{n}; Verizon {have.verizon_date.ne('').sum()}; "
          f"AT&T {have.att_date.ne('').sum()}; Sprint {have.sprint_date.ne('').sum()}; T-Mobile {have.tmobile_date.ne('').sum()}")
missing_top100 = pop.head(100)[~pop.head(100).CBSA.isin(onset.cbsa_code)]
print("top-100 metros with NO date:", missing_top100[["CBSA", "NAME"]].values.tolist())
t150 = pop.head(150)
m = onset[onset.cbsa_code.isin(t150.CBSA)]
print("top-150 missing Verizon:", sorted(t150[~t150.CBSA.isin(m[m.verizon_date.ne('')].cbsa_code)].NAME.tolist()))
print("top-150 missing AT&T:", sorted(t150[~t150.CBSA.isin(m[m.att_date.ne('')].cbsa_code)].NAME.tolist()))
print(long.groupby("carrier").size().to_string())
print(long.groupby(["carrier", "confidence"]).size().to_string())
