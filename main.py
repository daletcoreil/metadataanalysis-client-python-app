import os
import json
import boto3 as boto3
from pprint import pprint
import metadataanalysis_client
from botocore.config import Config

# Read configuration from json file.
with open(os.environ['APP_CONFIG_FILE']) as json_file:
    config_file = json.load(json_file)

configuration = metadataanalysis_client.Configuration()
if 'host' in config_file:
    configuration.host = config_file['host']

client = config_file['clientKey']
secret = config_file['clientSecret']
project_service_id = config_file['projectServiceId']

aws_access_key_id = config_file['aws_access_key_id']
aws_secret_access_key = config_file['aws_secret_access_key']
region_name = config_file['bucketRegion']

#aws_session_token = config_file['aws_session_token']

# Create an S3 client
# https://github.com/boto/boto3/issues/1644
# This is very important to initialize s3 client with region name, addressing_style & signature_version
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name, config=Config(s3={'addressing_style': 'path'}, signature_version='s3v4'))

# input & output data
bucketName = config_file['bucketName']

jsonInputFile = config_file['localPath'] + config_file['jsonInputFile']
jsonInputKey = config_file['jsonInputFile']

ttmlInputFile = config_file['localPath'] + config_file['ttmlInputFile']
ttmlInputKey = config_file['ttmlInputFile']

dpttOutputFile= config_file['localPath'] + config_file['dpttOutputFile']
dpttOutputKey = config_file['dpttOutputFile']

draftjsOutputFile = config_file['localPath'] + config_file['draftjsOutputFile']
draftjsOutputKey = config_file['draftjsOutputFile']

ttmlOutputFile = config_file['localPath'] + config_file['ttmlOutputFile']
ttmlOutputKey = config_file['ttmlOutputFile']

textOutputFile = config_file['localPath'] + config_file['textOutputFile']
textOutputKey = config_file['textOutputFile']

def download_segment_result_from_s3():
    pprint('Downloading result from S3 ...')
    s3.download_file(bucketName, dpttOutputKey, dpttOutputFile)
    s3.download_file(bucketName, draftjsOutputKey, draftjsOutputFile)
    pprint('Result was downloaded from s3')

def download_translate_result_from_s3():
    pprint('Downloading result from S3 ...')
    s3.download_file(bucketName, ttmlOutputKey, ttmlOutputFile)
    s3.download_file(bucketName, textOutputKey, textOutputFile)
    pprint('Result was downloaded from s3')

def delete_segment_artifacts_from_s3():
    pprint('Deleting s3 artifacts ...')
    s3.delete_object(Bucket=bucketName, Key=jsonInputKey)
    s3.delete_object(Bucket=bucketName, Key=dpttOutputKey)
    s3.delete_object(Bucket=bucketName, Key=draftjsOutputKey)
    pprint('S3 artifacts were deleted')

def delete_translate_artifacts_from_s3():
    pprint('Deleting s3 artifacts ...')
    s3.delete_object(Bucket=bucketName, Key=ttmlInputKey)
    s3.delete_object(Bucket=bucketName, Key=ttmlOutputKey)
    s3.delete_object(Bucket=bucketName, Key=textOutputKey)
    pprint('S3 artifacts were deleted')

def get_signed_url_input(inputKey):
    return s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucketName,
            'Key': inputKey
        },
        ExpiresIn=60*60)

def get_signed_url_output(outputKey):
    return s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': bucketName,
            'Key': outputKey
        },
        ExpiresIn=60 * 60)

def create_segment_text_request(signed_url_input_json, signed_url_otput_dptt, signed_url_otput_draftjs) -> metadataanalysis_client.SegmentTextRequest:
    json_input_file: Locator = metadataanalysis_client.Locator(bucketName, jsonInputKey, signed_url_input_json)
    dpttFormat: Locator = metadataanalysis_client.Locator(bucketName, dpttOutputKey, signed_url_otput_dptt)
    draftjsFormat: Locator = metadataanalysis_client.Locator(bucketName, draftjsOutputKey, signed_url_otput_draftjs)

    output_location: SegmentTextResponse = metadataanalysis_client.SegmentTextResponse(dpttFormat, draftjsFormat)
    segment_text_request = metadataanalysis_client.SegmentTextRequest(input_file=json_input_file,
                                                                      output_location=output_location)
    return segment_text_request

def create_translate_captions_request(signed_url_input_ttml, signed_url_otput_ttml, signed_url_otput_text, target_language) -> metadataanalysis_client.TranslateCaptionsRequest:
    ttml_input_file: Locator = metadataanalysis_client.Locator(bucketName, ttmlInputKey, signed_url_input_ttml)
    ttmlFormat: Locator = metadataanalysis_client.Locator(bucketName, ttmlOutputKey, signed_url_otput_ttml)
    textFormat: Locator = metadataanalysis_client.Locator(bucketName, textOutputKey, signed_url_otput_text)

    output_location: TranslateCaptionsResponse = metadataanalysis_client.TranslateCaptionsResponse(ttmlFormat, textFormat)
    translate_captions_request = metadataanalysis_client.TranslateCaptionsRequest(source_subtitle=ttml_input_file,
                                                                                  output_location=output_location,
                                                                                  target_language=target_language)
    return translate_captions_request


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

        # Upload json to S3
        pprint('Uploading json file to S3 ...')
        s3.upload_file(jsonInputFile, bucketName, jsonInputKey)
        pprint('JSON file was uploaded to s3')

        # Get signed urls
        pprint('Receiving signed urls ...')
        json_input_url = get_signed_url_input(jsonInputKey)
        output_url_dptt = get_signed_url_output(dpttOutputKey)
        output_url_draftjs = get_signed_url_output(draftjsOutputKey)

        pprint('input_url json:')
        pprint(json_input_url)
        pprint('output_url dptt:')
        pprint(output_url_dptt)
        pprint('output_url draftjs:')
        pprint(output_url_draftjs)

        pprint('Segmenting text ...')
        segment_text_request = create_segment_text_request(json_input_url, output_url_dptt, output_url_draftjs)
        segment_text_response = metadata_analysis_api.segment_text(project_service_id, segment_text_request)
        pprint(segment_text_response)

        # Download segment text result
        download_segment_result_from_s3()

        # Delete segment text artifacts
        delete_segment_artifacts_from_s3()

        # Upload ttml to S3
        pprint('Uploading ttml file to S3 ...')
        s3.upload_file(ttmlInputFile, bucketName, ttmlInputKey)
        pprint('JSON file was uploaded to s3')

        # Get signed urls
        pprint('Receiving signed urls ...')
        ttml_input_url = get_signed_url_input(ttmlInputKey)
        output_url_ttml = get_signed_url_output(ttmlOutputKey)
        output_url_text = get_signed_url_output(textOutputKey)

        pprint('ttml_input_url:')
        pprint(ttml_input_url)
        pprint('output_url ttml:')
        pprint(output_url_ttml)
        pprint('output_url text:')
        pprint(output_url_text)

        pprint('Translating captions ...')
        target_language = "RU"
        translate_captions_request = create_translate_captions_request(ttml_input_url, output_url_ttml, output_url_text, target_language)
        translate_captions_response = metadata_analysis_api.translate_captions(project_service_id, translate_captions_request)
        pprint(translate_captions_response)

        # Download translate captions result
        download_translate_result_from_s3()

        # Delete translate captions artifacts
        delete_translate_artifacts_from_s3()

        # """
    except ApiException as e:
        print("Exception when calling api: %s\n" % e)


main()
