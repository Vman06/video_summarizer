from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(test_video_id):
    yt = YouTubeTranscriptApi()

    transcript_list = yt.list(test_video_id)

    available_transcripts = []
    for transcript in transcript_list:
        available_transcripts.append({
            'language': transcript.language,
            'language_code': transcript.language_code,
            'is_generated': transcript.is_generated
        })
        print(transcript.language, transcript.language_code, transcript.is_generated)


    fetched_transcript = yt.fetch(test_video_id)

    # is iterable
    for snippet in fetched_transcript:
        print(snippet.text)

    # indexable
    last_snippet = fetched_transcript[-1]

    # provides a length
    snippet_count = len(fetched_transcript)


    return snippet_count

response = get_transcript("btPdx63uPIM")
print(response)

