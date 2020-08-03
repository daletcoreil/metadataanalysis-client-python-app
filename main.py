import os
import json
from pprint import pprint
import metadataanalysis_client

# Read configuration from json file.
with open(os.environ['APP_CONFIG_FILE']) as json_file:
    config_file = json.load(json_file)

configuration = metadataanalysis_client.Configuration()
if 'host' in config_file:
    configuration.host = config_file['host']

client = config_file['clientKey']
secret = config_file['clientSecret']
project_service_id = config_file['projectServiceId']

def main():
    try:
        # Get access token for this client.
        pprint('Retrieving access tokens ...')
        auth_api: AuthApi = metadataanalysis_client.AuthApi(metadataanalysis_client.ApiClient(configuration))
        token: Token = auth_api.get_access_token(client, secret)
        pprint(token)

        configuration.api_key['Authorization'] = token.authorization

        pprint('Analyze ...')
        analyze_request: AnalyzeRequest = metadataanalysis_client.AnalyzeRequest(text="President Donald Trump tried to explain his agitating app roach to life, politics and the rest of the world in a flash of impatience during a blustery news conference in France.   It's the way I negotiate. It's done me well over the years and it's doing even better for the country, I think,  he said.",
                                                                                 extractors=["entities", "topics"],
                                                                                 extractors_score_threshold=0.5,
                                                                                 classifiers=["IPTCNewsCodes", "IPTCMediaTopics"],
                                                                                 classifier_score_threshold=0.5)
        metadata_analysis_api: MetadataAnalysisApi = metadataanalysis_client.MetadataAnalysisApi(metadataanalysis_client.ApiClient(configuration))
        analyzed_text_response: AnalyzedTextResponse = metadata_analysis_api.analyze(project_service_id, analyze_request)
        pprint(analyzed_text_response)

        pprint('Knowledge graph search ...')
        ids = [entity.mid for entity in analyzed_text_response.entities if entity.mid is not None]
        knowledge_graph_search_response: KnowledgeGraphSearchResponse = metadata_analysis_api.knowledge_graph_search(project_service_id, ids)
        pprint(knowledge_graph_search_response)

        pprint('Translating text ...')
        translate_text_request = metadataanalysis_client.TranslateTextRequest(
            text="President Donald Trump tried to explain his agitating app roach to life.",
            target_language="RU"
        )
        translate_text_response = metadata_analysis_api.translate_text(project_service_id, translate_text_request)
        pprint(translate_text_response)

        # """
    except ApiException as e:
        print("Exception when calling api: %s\n" % e)


main()
