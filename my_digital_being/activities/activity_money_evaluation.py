import logging
from typing import Dict, Any
from framework.activity_decorator import activity, ActivityBase, ActivityResult
from skills.skill_chat import chat_skill

logger = logging.getLogger(__name__)

@activity(
    name="MoneyEvaluationActivity",
    energy_cost=0.3,
    cooldown=43200,  # 12 hours
    required_skills=["openai_chat"],
)
class MoneyEvaluationActivity(ActivityBase):
    """
    Activity that evaluates potential money-making ideas, considering feasibility,
    risks, and alignment with ethical principles.
    """

    def __init__(self):
        super().__init__()
        self.system_prompt = """You are an AI that evaluates potential money-making ideas.
        Consider feasibility, market potential, resource requirements, risks, and ethical implications.
        Provide a structured analysis covering:
        - Idea feasibility
        - Resource requirements
        - Market potential
        - Risk assessment
        - Ethical considerations
        Keep responses practical and grounded in reality.
        """

    async def execute(self, shared_data) -> ActivityResult:
        try:
            logger.info("Starting MoneyEvaluationActivity...")

            if not await chat_skill.initialize():
                return ActivityResult(
                    success=False, error="Failed to initialize openai_chat skill"
                )

            # Generate some initial ideas to evaluate
            ideas_prompt = """Generate 3 potential money-making ideas that align with 
            current market trends and technological capabilities. Consider both traditional 
            and innovative approaches."""

            ideas_response = await chat_skill.get_chat_completion(
                prompt=ideas_prompt,
                system_prompt=self.system_prompt,
                max_tokens=200
            )

            if not ideas_response["success"]:
                return ActivityResult(success=False, error=ideas_response["error"])

            generated_ideas = ideas_response["data"]["content"]

            # Evaluate the generated ideas
            evaluation_prompt = f"""Analyze these potential money-making ideas:

            {generated_ideas}

            Provide a detailed evaluation of each idea, considering:
            1. Feasibility and implementation requirements
            2. Potential market size and demand
            3. Required resources and initial investment
            4. Possible risks and challenges
            5. Ethical considerations and social impact
            """

            evaluation_response = await chat_skill.get_chat_completion(
                prompt=evaluation_prompt,
                system_prompt=self.system_prompt,
                max_tokens=500
            )

            if not evaluation_response["success"]:
                return ActivityResult(success=False, error=evaluation_response["error"])

            evaluation = evaluation_response["data"]["content"]

            return ActivityResult(
                success=True,
                data={
                    "generated_ideas": generated_ideas,
                    "evaluation": evaluation
                },
                metadata={
                    "model": evaluation_response["data"]["model"],
                    "finish_reason": evaluation_response["data"]["finish_reason"],
                },
            )

        except Exception as e:
            logger.error(f"Error in MoneyEvaluationActivity: {e}")
            return ActivityResult(success=False, error=str(e))