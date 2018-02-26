from urllib2 import urlopen
import xml.etree.ElementTree as ET
import pandas as pd


url = "http://syndication.enterprise.websiteidx.com/feeds/BoojCodeTest.xml"
required_fields = ['MlsId','MlsName','DateListed','StreetAddress','Price',\
                   'Bedrooms','Bathrooms','FullBathrooms','HalfBathrooms',\
                   'ThreeQuarterBathrooms','Appliances','Rooms','Description']


class XML_to_CSV(object):


    def __init__(self, xml_url):

        response = urlopen(xml_url)
        tree = ET.parse(response)
        root = tree.getroot()
        self.listing_elements = root.findall('Listing')
        self.make_csv()

        return


    def get_property_details(self):
        '''Retrieves the required fields for the CSV and compiles them into
        a dictionary.'''

        property_details = {}

        for i, listing in enumerate(self.listing_elements):
            e = self.listing_elements[i]

            # All 'ListingDetails' sub-elements
            mls_id = self.get_element_text(e,'ListingDetails','MlsId')
            mls_name = self.get_element_text(e,'ListingDetails','MlsName')
            date_listed = self.get_element_text(e,'ListingDetails','DateListed')
            price = self.get_element_text(e,'ListingDetails','Price')

            # All 'Location' sub-elements
            street_address = self.get_element_text(e,'Location','StreetAddress')

            # All 'BasicDetails' sub-elements
            beds = self.get_element_text(e,'BasicDetails','Bedrooms')
            baths = self.get_element_text(e,'BasicDetails','Bathrooms')
            full_bath = self.get_element_text(e,'BasicDetails','FullBathrooms')
            half_bath = self.get_element_text(e,'BasicDetails','HalfBathrooms')
            three_qtr_bath = self.get_element_text(e,'BasicDetails','ThreeQuarterBathrooms')
            description = self.get_element_text(e,'BasicDetails','Description')

            # All 'RichDetails' sub-elements
            appliances = self.get_element_text(e,'RichDetails','Appliances','Appliance')
            rooms = self.get_element_text(e,'RichDetails','Rooms','Room')

            property_details[i] = {'MlsId':mls_id,
                                   'MlsName':mls_name,
                                   'DateListed':pd.to_datetime(date_listed),
                                   'StreetAddress':street_address,
                                   'Price':price,
                                   'Bedrooms':beds,
                                   'Bathrooms':baths,
                                   'FullBathrooms':full_bath,
                                   'HalfBathrooms':half_bath,
                                   'ThreeQuarterBathrooms':three_qtr_bath,
                                   'Appliances':appliances,
                                   'Rooms':rooms,
                                   'Description':str(description)[:200]}
        return property_details


    def make_df(self):
        '''Constructs a DataFrame that is masked with the requested CSV
        requirements. The DataFrame contains only properties listed from 2016
        and that have the word "and" in the Description field. It is ordered
        by DateListed.'''

        property_details_dict = self.get_property_details()
        property_details_df = pd.DataFrame(property_details_dict).T

        # DataFrame masks
        desc_and = [True if 'and' in description else False \
                    for description in property_details_df['Description']]
        date_mask = [True if date.year == 2016 else False \
                     for date in property_details_df['DateListed']]

        updated_pd_df = property_details_df[desc_and]
        updated_pd_df = property_details_df[date_mask]

        # Organizing the columns
        updated_pd_df = updated_pd_df[required_fields]

        return updated_pd_df.sort_values('DateListed')


    def make_csv(self):
        '''Converts DataFrame to CSV.'''

        final_df = self.make_df()
        final_df.to_csv('final_csv.csv')
        return


    def get_element_text(self, *args):
        '''Retrieves the specific element text. Args should be first the
        element, then the parent node, then the child nope, and optionally a
        grandchild node.'''

        element = args[0]
        parent = args[1]
        child = args[2]

        if len(args) == 4:
            grandchild = args[3]
            e = element.find(parent).find(child)

            try:
                e.findall(grandchild)
            except:
                e_txt = str(e)
            else:
                e_txt = []
                for child in e.findall(grandchild):
                    e_txt.append(child.text)
                e_txt = ','.join(e_txt)

        else:
            e = element.find(parent).find(child)

            try:
                e_txt = e.text
            except:
                e_txt = str(e)
            else:
                e_txt = e.text

        return e_txt


    def parse_details(self, n_listings=1):
        '''Prints out the element tags and text of a specified number of
        listings.'''

        count = 0
        for home in self.listing_elements:
            for detail in list(home):
                print '\n----------------\n', detail.tag, '\n----------------\n'

                for sub_detail in list(detail):
                    if sub_detail.text == '\n\t' or sub_detail.text == '\n':
                        sub_tag_text = [{sub_text.tag: sub_text.text}
                                        for sub_text in sub_detail[:]]
                        print '{}: "{}"'.format(sub_detail.tag, sub_tag_text)
                    else:
                        print '{}: "{}"'.format(sub_detail.tag, sub_detail.text)

            count += 1
            if count >= n_listings:
                return


x2c = XML_to_CSV(url)
read_pd_df = pd.read_csv('final_csv.csv', index_col=0)
print read_pd_df
