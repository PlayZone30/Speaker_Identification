from more_itertools.more import sample
from openai import OpenAI


class SpeakerIdentifier:
    def __init__(self, api_key, base_url="https://openrouter.ai/api/v1"):
        """
        Initialize the OpenRouter client for speaker identification

        :param api_key: OpenRouter API key
        :param base_url: OpenRouter API base URL
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.system_prompt="""
            # Speaker Identification Task

            ## Objective
            Accurately map anonymous speaker labels (Speaker 0, Speaker 1, etc.) to their actual names based on the context of the conversation, accounting for cases where multiple speakers may share the same microphone.
            
            ## Core Requirements
            - Carefully analyze the entire transcript.
            - Identify all unique speakers, even when multiple individuals share a single speaker label.
            - Map speaker labels to their correct names, listing multiple names per label if necessary.
            - Provide detailed reasoning for each mapping.
            - Handle complex conversation scenarios, including shared microphones and subtle speaker transitions.
            
            ## Detailed Instructions
            1. Analyze the full transcript thoroughly.
            2. Look for direct name mentions within dialogues.
            3. Observe conversation patterns and interaction styles.
            4. Pay attention to:
               - Who asks questions
               - Who provides responses
               - Contextual cues about each speaker’s role
               - Specific domain or project references
            5. **Handling Multiple Speakers on One Mic:**
               - If a speaker label (e.g., Speaker 0) appears to capture different individuals (e.g., due to microphone sharing), identify and list all names associated with that label.
               - Use contextual cues to detect speaker changes within the same label, such as:
                 - **Addressing after statements**: Phrases like "Thank you, [Name]" or "Great, [Name]" immediately following a statement, indicating [Name] was the speaker.
                 - **Explicit handovers**: Statements like "Over to you, [Name]" suggesting [Name] speaks next.
                 - **Self-identifications**: Phrases like "This is [Name] speaking."
                 - **Introductions**: Statements like "Hi, I’m [Name]" or moderator cues such as "Now, [Name] will speak."
                 - **Shifts in topic, tone, or style**: Changes that may suggest a different speaker.
               - Include all identified names in the `speaker_mapping` as a list for that label.
            6. **Speaker Count Consideration:**
               - Typically, transcripts include 4 speaker labels (e.g., Speaker 0 to Speaker 3). However, up to 6 unique speakers may be present if additional individuals speak through existing microphones.
               - Identify and map all unique speakers, associating multiple names with a single label if needed, rather than creating new speaker labels beyond those provided.
            
            ## Output Format
            Provide output strictly in this JSON format:
            ```json
            {
                "speaker_mapping": {
                    "Speaker 0": ["Name1", "Name2", ...],
                    "Speaker 1": ["Name3"]
                },
                "confidence_scores": {
                    "Speaker 0": [score1, score2, ...],
                    "Speaker 1": [score3]
                },
                "reasoning": {
                    "Speaker 0": "Explanation for each name associated with Speaker 0.",
                    "Speaker 1": "Explanation for the mapping."
                }
            }
            -speaker_mapping: Map each speaker label to a list of names. Use a single-element list if only one name is identified.
            -confidence_scores: Provide a list of confidence scores corresponding to each name in the mapping.
            -reasoning: Detail the evidence for each name under a speaker label.
            
            Important Guidelines
            If certainty is not 100%, provide the most likely mapping based on context.
            When a speaker label corresponds to multiple names, list all names in an array and assign individual confidence scores.
            Do not create new speaker labels (e.g., Speaker 4) beyond those in the transcript; instead, associate additional speakers with existing labels.
            Ensure output is valid JSON.
            
            Consider:
            Dialogue flow
            Technical discussions
            Project references
            Interaction patterns
            Explain reasoning clearly and systematically.
            
            Challenging Scenarios to Handle:
            Minimal name mentions.
            Similar conversation styles among speakers.
            Complex multi-person discussions.
            Technical or domain-specific conversations.
            Multiple speakers sharing a microphone, requiring detection of subtle cues.
            
            Confidence Levels:
            0.9-1.0: High confidence (near certain)
            0.7-0.89: Moderate confidence (strong evidence)
            0.5-0.69: Low confidence (potential mapping)
            <0.5: Insufficient evidence
            
            Additional Notes:
            Be logical and systematic in your approach.
            When in doubt, provide multiple interpretations with confidence levels.
            Ensure all unique speakers are mapped, even if they share microphones with others.
            
        """
    def identify_speakers(self, transcript_chunk, model="meta-llama/llama-3.3-70b-instruct:free"):
        """
        Identify speakers in a transcript chunk

        :param transcript_chunk: A chunk of the meeting transcript
        :param model: OpenRouter model to use
        :return: Speaker mapping result for the chunk
        """
        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "",
                    "X-Title": ""
                },
                model=model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Analyze and map speakers in this transcript:\n{transcript_chunk}"}
                ],
                response_format={"type": "json_object"}
            )

            # Check if the response structure is as expected
            if not completion or not hasattr(completion, "choices") or not completion.choices:
                print("Unexpected API response structure:", completion)
                return None

            result = completion.choices[0].message.content
            return result

        except Exception as e:
            print(f"Error in speaker identification: {e}")
            return None








