import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from dataclasses import dataclass
from typing import Dict, Any, Optional

# Create minimal test doubles for required framework classes
@dataclass
class ActivityResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ActivityBase:
    def __init__(self):
        pass

def activity(name, energy_cost, cooldown, required_skills):
    def decorator(cls):
        cls.name = name
        cls.energy_cost = energy_cost
        cls.cooldown = cooldown
        cls.required_skills = required_skills
        return cls
    return decorator

# Create a mock chat_skill
class MockChatSkill:
    async def initialize(self):
        return True

    async def get_chat_completion(self, prompt, system_prompt, max_tokens):
        return {
            "success": True,
            "data": {
                "content": "Mock response",
                "model": "gpt-4",
                "finish_reason": "stop"
            }
        }

chat_skill = MockChatSkill()

# Now define the activity class
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
            return ActivityResult(success=False, error=str(e))

# Tests
@pytest.mark.asyncio
async def test_money_evaluation_activity():
    """Test the MoneyEvaluationActivity execution and output format"""
    
    # Mock chat skill responses
    mock_ideas_response = {
        "success": True,
        "data": {
            "content": """1. Online Course Creation Platform
2. AI-Powered Personal Finance App
3. Sustainable Product Marketplace""",
            "model": "gpt-4",
            "finish_reason": "stop"
        }
    }
    
    mock_evaluation_response = {
        "success": True,
        "data": {
            "content": """Analysis of money-making ideas:

1. Online Course Creation Platform
- Feasibility: High, leverages existing technologies
- Market: Growing e-learning sector
- Resources: Medium initial investment
- Risks: Competitive market
- Ethics: Positive educational impact

2. AI-Powered Personal Finance App
- Feasibility: Medium, requires technical expertise
- Market: High demand for financial tools
- Resources: Significant development costs
- Risks: Data security concerns
- Ethics: Privacy considerations important

3. Sustainable Product Marketplace
- Feasibility: Medium-high
- Market: Growing eco-conscious consumer base
- Resources: Platform development and vendor network
- Risks: Supply chain management
- Ethics: Positive environmental impact""",
            "model": "gpt-4",
            "finish_reason": "stop"
        }
    }

    # Create patches for the chat skill
    with patch.object(chat_skill, 'initialize', new_callable=AsyncMock) as mock_init:
        with patch.object(chat_skill, 'get_chat_completion', new_callable=AsyncMock) as mock_chat:
            # Set up mock returns
            mock_init.return_value = True
            mock_chat.side_effect = [mock_ideas_response, mock_evaluation_response]
            
            # Initialize and execute the activity
            activity = MoneyEvaluationActivity()
            result = await activity.execute({})
            
            # Verify the activity executed successfully
            assert result.success is True, "Activity execution failed"
            
            # Verify the output structure
            assert "generated_ideas" in result.data, "Missing generated ideas in output"
            assert "evaluation" in result.data, "Missing evaluation in output"
            
            # Verify metadata
            assert "model" in result.metadata, "Missing model information"
            assert "finish_reason" in result.metadata, "Missing finish reason"
            
            # Verify chat skill was called correctly
            assert mock_init.called, "Chat skill was not initialized"
            assert mock_chat.call_count == 2, "Expected two chat completions"

@pytest.mark.asyncio
async def test_money_evaluation_activity_error_handling():
    """Test error handling in MoneyEvaluationActivity"""
    
    # Test initialization failure
    with patch.object(chat_skill, 'initialize', new_callable=AsyncMock) as mock_init:
        mock_init.return_value = False
        
        activity = MoneyEvaluationActivity()
        result = await activity.execute({})
        
        assert result.success is False, "Activity should fail when initialization fails"
        assert "Failed to initialize" in result.error, "Wrong error message"

    # Test chat completion failure
    with patch.object(chat_skill, 'initialize', new_callable=AsyncMock) as mock_init:
        with patch.object(chat_skill, 'get_chat_completion', new_callable=AsyncMock) as mock_chat:
            mock_init.return_value = True
            mock_chat.return_value = {"success": False, "error": "API error"}
            
            activity = MoneyEvaluationActivity()
            result = await activity.execute({})
            
            assert result.success is False, "Activity should fail when chat completion fails"
            assert result.error is not None, "Error message should be present"