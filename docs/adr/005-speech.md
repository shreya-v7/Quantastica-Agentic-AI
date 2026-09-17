# ADR 005: Speech

Status: accepted

`SpeechProvider` with Sarvam primary and Transcribe/Polly as the AWS fallback. CI uses
`MockSpeech`. Utterances become text events or queue queries. TTS may only speak rupees
that already exist on exception rows.
