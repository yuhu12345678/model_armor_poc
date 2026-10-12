Requirements:
* Set up a Google Cloud Model Armor integration (sanitization/guardrails for prompts & responses)
* Integrate Model Armor with the LiteLLM proxy or custom pre/post-call hooks
* Create a client or test script to interact with the Model Armor API

Technical:
* Use terraform to setup Model Armor template
* Generate sample config.yaml for litellm integration
* Write python scripts for testing integration
* Use promptfoo for more testing
* Create another set of tests in deepeval for evaluating the prompts we created with promptfoo. I would like to use both deepeval and promptfoo to setup framework to build and evaluate gold dataset currently in BQ (dumped from Langfuse).