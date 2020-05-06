import pandas as pd
import urllib.request
import urllib.parse
import json
import time
from datetime import datetime
from tqdm import tqdm
import csv

class APIResponse:

    def __init__(self, url_file):

        # Create full contents response dictionary
        self.contents_obj = {}

        self.contents_obj['desktop'] = []

        self.url_list, self.df_urls = self.load_urls(url_file)

       

    def get_contents_obj(self):
        '''
        Request response object for each url and store as json.
        '''

        data_file = open('data_file.csv', 'w') 

        csv_writer = csv.writer(data_file)

        count = 0

        for i in tqdm(range(0, len(self.df_urls))):
            success = False

            for j in range(0, 3):
                try:
                    print('Requesting row #:', i)
                    print('Try #:', j)
                    if count == 0: 
                          # Writing headers of CSV file 
                        csv_writer.writerow(["people_id", "url", "desktop_score","mobile_score"]) 
                        count += 1

                    url = self.df_urls.iloc[i]['URL']
                    people_id = int(self.df_urls.iloc[i]['people_id'])
                    escaped_url = urllib.parse.quote(url)

                    device_type = self.df_urls.iloc[i]['device_type']

                    contents = urllib.request.urlopen(
                        'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={}&strategy={}'\
                        .format(escaped_url, device_type)
                    ).read().decode('UTF-8')

                    mobile_contents = urllib.request.urlopen(
                        'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={}&strategy={}'\
                        .format(escaped_url, 'mobile')
                    ).read().decode('UTF-8')

                    contents_json = json.loads(contents)

                    mobile_contents_json = json.loads(mobile_contents)

                    google_data = {}
                    google_data['desktop_score']=contents_json["lighthouseResult"]["categories"]["performance"]["score"] * 100
                    google_data['mobile_score']=mobile_contents_json["lighthouseResult"]["categories"]["performance"]["score"] * 100
                    google_data['url']=url
                    google_data['people_id']= people_id
                    #json_data = json.loads(google_data)
                    # Insert returned json response into full contents
                    #self.contents_obj[device_type][people_id]= google_data

                    csv_writer.writerow([google_data['people_id'],google_data['url'],google_data['desktop_score'],google_data['mobile_score']])

                    self.contents_obj[device_type].append(google_data)

                    success = True

                except Exception as e:
                    if 'Internal Server Error' in str(e):
                        print('Error:', e)
                        print("Error getting response. Sleeping for 5 seconds. Try #%d"%j)
                        time.sleep(5)
                    
                    else:
                        print('Error:', e)
                        print("Error getting response. Sleeping for 1 hour.Try #%d"%j)
                        time.sleep(10)

                if success:
                    break

        #self.contents_obj[device_type]= res_data   
        # 
        data_file.close()      

        # Save json response
        self.save_contents_to_file(self.contents_obj)

        return self.contents_obj


    def load_urls(self, url_file):
        '''
        Import list of urls.
        '''
        df_urls = pd.read_csv(url_file)
        urls_col = df_urls['URL']
        url_list = urls_col.tolist()

        return url_list, df_urls

    def save_contents_cummulatively(self, contents):
        with open('{}-cummulative_response.json'.format(datetime.now().strftime("%Y-%m-%d")), 'w') as outfile:
            json.dump(contents, outfile, indent=4)

    def save_contents_to_file(self, contents):
        with open('{}-response.json', 'w') as outfile:
            json.dump(contents, outfile, indent=4)
