# LLM Agent Constructor

<details open>
<summary>Table of Contents</summary>
<blockquote>

## Table of Contents

- [LLM Agent Constructor](#llm-agent-constructor)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Predefined agents](#predefined-agents)
      - [System analyst](#system-analyst)
    - [Custom agents creation](#custom-agents-creation)
  - [Further works](#further-works)

</blockquote>
</details>

<details open>
<summary>Installation</summary>
<blockquote>

## Installation

To install the project:

1. Clone the repository
2. Install poetry
    ```bash
    pip install poetry==1.8.4
    ```
3. Install the dependencies
    ```bash
    poetry install
    ```
4. Set up the environment variables
    ```
    OPENAI_API_KEY=<your-api-key>
    OPENAI_URL=<api-url>
    ``` 

</blockquote>
</details>


<details open>
<summary>Usage</summary>
<blockquote>

## Usage

<details open>
<summary>Predefined agents</summary>
<blockquote>

### Predefined agents


<details open>
<summary>System analyst</summary>
<blockquote>

#### System analyst
We have already predefined the system analyst agent. To run it, just use the following command:
```bash
python -m src.run
```

This agent will start the interview with the user and will try to understand the user's needs and preferences. As result you will have 12 files.

The most useful files are:
- 7_translated_report.md – report with your system definition;
- 8_testing_stories.md – imagine stories of your customers using your system that can be used for integration testing and better understanding;
- 9_use_cases.md – use cases of your system that can be used for further development;
- 11_domain_model.md – domain model of your system that can be used for further classes diagram creation.

Full system analyst process can be explained in the following diagram:

![System analyst process](./docs/SystemAnalystPipeline.png)


</blockquote>
</details>

</blockquote>
</details>

<details open>
<summary>Custom agents creation</summary>
<blockquote>

### Custom agents creation

To create your own agent, you need to define a new instance of the `src.core.pipeline.Pipeline` class.

You can see the example in `src/core/system_analyst.py`.

Then just go to the main function in `src/run.py` and add replace currently using pipeline with yours.


</blockquote>
</details>

</blockquote>
</details>


<details open>
<summary>Further works</summary>
<blockquote>

## Further works

In next releases we wants to add:
1. API, separately graphs storing and processing;
2. More agent types with different purposes;
3. Web interface for easier usage;
4. Creating private agent graphs for personal usage.

</blockquoute>
</details>



