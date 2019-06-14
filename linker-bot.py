from __future__ import annotations
import requests
import json
import yaml
import argparse
from typing import List
import dsl_parser.dsl_parser as dl
from dsl_parser.cdf import CDF
from functools import reduce

get_query = """
query{
  measurables(first:10){
    total
    edges{
      node{
        id
      }
    }
  }
}
"""

#TODO: Write logic for parsing and formatting returned CDF from JSON
#TODO: Better way of building GraphQL Queries


def get_measurement_from_measurable(mId):
    return f"""
        query {{
        measurements(first:10, measurableId: {mId}){{
            total
        }}
        }}
        """


def get_all_measurables_select_one():
    measurable_json = run_query(get_query)
    measurables = measurable_json['data']['measurables']['edges']
    return measurables[0]['node']['id']


def run_query(query):
    request = requests.post(FORETOLD_API,
                            json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(
            request.status_code, query))


class Bot():
    """
    Generic Bot Class for interacting with the foretold API. Holds the query methods and API tokens.
    """

    def __init__(self, api_url, bot_token, agent_id, *args, **kwargs):
        self.api_url = api_url
        self.bot_token = bot_token
        self.agent_id = agent_id
        return super().__init__(*args, **kwargs)

    def query(self, q: str):
        """
        Business logic for graphql querys
        """
        request = requests.post(self.api_url,
                                json={'query': q}, headers={"Authorization": "Bearer {}".format(self.bot_token)})
        if request.status_code == 200:
            return request.json()
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(
                request.status_code, q))

    def query_multiple(self, targets, query) -> List:
        """
        Takes N targets and M Queries and runs for each target all the provided queries
        Returns list of JSON
        """
        # Currently unoptimized for distributed failures and blocking
        # TODO: push to async queue
        # TODO: Modify exception handling to prevent one failure from blocking all
        # TODO: Modify to apply params to get query
        queries_to_run = [query(t) for t in targets]
        return [self.query(q) for q in queries_to_run]

    def poll(self):
        """
        Implements method to check if should query based on external subscription or time based event
        """
        pass


class LinkerBot(Bot):
    """
    Linker Bot takes in:
    - one user defined foretold measurable to update (m)
    - N configurable other measurables
    - a user schema for how they should interact
    """

    def __init__(self, measurable, measurables: List, *args, **kwargs):
        self.measurable = measurable
        self.measurables = measurables
        self.ucl = "dsl_parser/test.txt"
        return super().__init__(*args, **kwargs)

    def generate_mutation(self, CDF, measurable_id) -> str:
        return f"""mutation {{
        measurementCreate(input: {{
                    value: {CDF},
                    competitorType: COMPETITIVE,
                    agentId: "{self.agent_id}",
                    measurableId: "{measurable_id}"
                    }}) {{
                        id
                    }}
                }}
        """

    def get_measurable_cdf(self, id, first=1):
        return f"""
            query{{
            measurable(id: "{id}"){{
                name
                Measurements(first: {first}) {{
                edges {{
                    node {{
                        value {{
                        floatCdf {{
                            xs
                            ys
                        }}
                        }}
                    }}
                }}
                }}
            }}
            }}
                """

    def process_m_cdfs(self, response):
        """
        take in the response from get_measurable_cdfs queries, return CDF object
        """
        return [CDF(n["node"]["value"]["floatCdf"]["xs"], n["node"]["value"]["floatCdf"]["ys"]) for n in response["data"]["measurable"]["Measurements"]["edges"]]

    def user_combination_logic(self, m_cdfs):
        """
        This function takes in the user defined logic, provides the file loc to the parser, along w/ the values for the nodes.
        Returns new XS, YS

        """
        """measurable_cdfs[i] is a var(list) to send to the parser"""

        #Aggregate each measurable
        #TODO: Will change to allow more specificity

        agg_measurables = [
            reduce(lambda x, y: x.combine_cdf(y), m) for m in m_cdfs]
        nCDF = json.load(dl.interface(self.ucl, agg_measurables))
        #TODO: Change load pattern so returned json can be used for new CDF
        return nCDF['floatCDF']['xs'], nCDF['floatCDF']['ys']

    def get_agents_measurements_from_measurable(self, mId):
        return f"""
            query{{
                measurable(id: "{mId}"){{
                    name
                    Measurements {{
                    edges {{
                        node {{
                            agentId
                            value {{
                            floatCdf {{
                                xs
                                ys
                            }}
                            }}
                        }}
                    }}
                    }}
                }}
                }}
            """

    def process_agents_cdfs(self, response):
        for n in response["data"]["measurable"]["Measurements"]["edges"]:
            if n["node"]["agentId"] == self.agent_id:
                return CDF(n["node"]["value"]["floatCdf"]["xs"], n["node"]["value"]["floatCdf"]["ys"])
        return None

    def generate_sample_values(self):
        """Generates XS and YS from checking other measurables"""
        # creates a List(measurable) of List(measurements on that measurable) of CDFS
        #TODO this logic will need to be rewritten to handle async calls, and to separate into multiple functions
        responses = self.query_multiple(
            self.measurables, self.get_measurable_cdf)
        """List of List of CDFs, where the outer List is the Measurable and the Inner List is the CDF from the retrieved measurements"""
        """[[CDF, CDF][CDF, CDF]]"""
        return [self.process_m_cdfs(r) for r in responses]

    def alert_user_to_change(self):
        """Send an alert to the owner of the bot that there's been a change in one of their subscribed measurables"""
        pass

    def update(self):
        """
        Updates m
        """
        # Check all subscribed measurables
        # If there are changes to the previous value, do something
        # TODO: Add persistent storage
        q = self.get_agents_measurements_from_measurable(self.measurable)
        responses = self.query(q)
        cdf = self.process_agents_cdfs(responses)
        try:
            measurable_cdfs = self.generate_sample_values()
            xs, ys = self.user_combination_logic(measurable_cdfs)
            #TODO: Call user defined func
            nCDF = CDF(xs, ys)
            #TODO: Add equality check between lists
            if cdf == nCDF:
                return False, "No Changes Since Last Update"
            mutation = self.generate_mutation(nCDF, self.measurable)
            self.query(mutation)
        except:
            pass


def main():
    print("running main")
    try:
        with open("config.yml", 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
    except e as identifier:
        cfg = False
    if not cfg:
        # TODO assign args instead of cfg for cli
        # parser = argparse.ArgumentParser()
        cfg = None
    lb = LinkerBot(api_url=cfg['FORETOLD_API'], bot_token=cfg['BOT_TOKEN'], agent_id=cfg['AGENT_ID'],
                   measurable=cfg['MEASURABLE_PRIME'], measurables=cfg['MEASURABLES_SUBSCRIBED'])
    lb.update()


if __name__ == "__main__":
    main()
