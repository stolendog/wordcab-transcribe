from datetime import timedelta


def print_speech(segments: list) -> None:
    for segment in segments:
        startTime = str(0)+str(timedelta(seconds=int(segment.start)))+',000'
        endTime = str(0)+str(timedelta(seconds=int(segment.end)))+',000'
        text = segment.text
        s_text = f"{segment.id}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"
        print(s_text)