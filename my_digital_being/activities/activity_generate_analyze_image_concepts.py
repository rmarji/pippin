import logging
from typing import Dict, Any
from framework.activity_decorator import activity, ActivityBase, ActivityResult
from skills.skill_chat import chat_skill
from framework.api_management import api_manager

@activity(
    name="generate_analyze_image_concepts",
    energy_cost=0.7,
    cooldown=7200,
    required_skills=["image_generation", "openai_chat", "lite_llm"]
)
class GenerateAnalyzeImageConceptsActivity(ActivityBase):
    """Generate and analyze image concepts based on 'Test Primary Objective'"""

    def __init__(self):
        super().__init__()

    async def execute(self, shared_data) -> ActivityResult:
        try:
            logger = logging.getLogger(__name__)
            logger.info("Executing GenerateAnalyzeImageConceptsActivity")

            # Generate images using image_generation skill
            image_prompts = [
                "Test Primary Objective as a futuristic cityscape",
                "Test Primary Objective represented by abstract art",
                "Test Primary Objective in a natural landscape"
            ]
            generated_images = []
            for prompt in image_prompts:
                result = await api_manager.composio_manager.execute_action(
                    action="IMAGE_GENERATION_CREATE",
                    params={"prompt": prompt},
                    entity_id="MyDigitalBeing"
                )
                if result.success:
                    generated_images.append({"prompt": prompt, "image_url": result.data.get('url')})
                else:
                    logger.error(f"Failed to generate image for prompt: {prompt}")

            # Simulate conversations using openai_chat skill
            if not await chat_skill.initialize():
                return ActivityResult.error_result("Chat skill not available")
            conversation_prompt = "Discuss the challenges of testing objectives."
            conversation = await chat_skill.get_chat_completion(prompt=conversation_prompt)

            # Summarize and compare testing strategies using lite_llm skill
            strategy_texts = [
                "Strategy 1: Use automated testing tools for efficiency.",
                "Strategy 2: Incorporate user testing for real-world insights.",
                "Strategy 3: Perform extensive unit tests on all components."
            ]
            summarized_strategies = []
            for text in strategy_texts:
                summary_result = await api_manager.composio_manager.execute_action(
                    action="TEXT_SUMMARIZATION",
                    params={"text": text},
                    entity_id="MyDigitalBeing"
                )
                if summary_result.success:
                    summarized_strategies.append(summary_result.data.get('summary'))
                else:
                    logger.error(f"Failed to summarize strategy text: {text}")

            return ActivityResult.success_result({
                "generated_images": generated_images,
                "conversation": conversation,
                "summarized_strategies": summarized_strategies
            })

        except Exception as e:
            logger.exception("An error occurred during execution")
            return ActivityResult.error_result(str(e))