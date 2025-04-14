from more_itertools.more import sample
from openai import OpenAI


class Chunk:
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

        # Comprehensive system prompt for speaker identification
        # self.system_prompt = """
        #     Please consolidate the following partial speaker identification results into one final unified output. Your final output should include:
        #
        #     Objective: A brief statement describing the goal of accurately mapping anonymous speaker labels (e.g., Speaker 0, Speaker 1) to their actual names.
        #
        #     Analysis: A summary of the overall observations from the transcript, including any context about speaker roles and interactions.
        #
        #     Speaker Mapping: A clear mapping of each speaker label to its identified name.
        #
        #     Confidence Scores: Confidence scores for each mapping (values between 0 and 1) based on your analysis.
        #
        #     Reasoning: A detailed explanation of how each mapping was derived, including any key cues from the transcript.
        #     Please combine and refine these results to generate one final, coherent JSON output with the following structure:
        #
        #     json
        #     {
        #         "speaker_mapping": {
        #             "Speaker X": "Actual Name",
        #             ...
        #         },
        #         "confidence_scores": {
        #             "Speaker X": confidence_value,
        #             ...
        #         },
        #         "reasoning": {
        #             "Speaker X": "Explanation of mapping for Speaker X",
        #             ...
        #         }
        #     }
        #     Your final answer should also include an explanation of the process you used to combine the results.And you need to map all the speakers if don't know you can write unkown but you need to map all the speakers
        # """
        self.system_prompt="""
            map all the speakers form the given text 
            ## Output Format
            Your final answer should be in valid JSON format with the following structure:
            
            {
                "speaker_mapping": {
                    "Speaker X": "Name or Graph Representation",
                    ...
                },
                "confidence_scores": {
                    "Speaker X": confidence_value,
                    ...
                },
                "reasoning": {
                    "Speaker X": "Explanation of mapping for Speaker X",
                    ...
                },
                "consolidation_process": "A brief explanation of how the partial results were combined to form the final output."
            }
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
                    {"role": "user", "content": f"Analyze and map all the speakers in this transcript:\n{transcript_chunk}"}
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





