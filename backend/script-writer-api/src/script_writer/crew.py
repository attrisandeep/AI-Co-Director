from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool

@CrewBase
class ScriptWriter():
    """ScriptWriter crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config= 'config/agents.yaml'
    tasks_config= 'config/tasks.yaml'
    
    @agent
    def script_transformer(self) -> Agent:
        return Agent(
            config=self.agents_config['script_transformer'],
            verbose=True,
        )

    @agent
    def quality_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['quality_editor'], 
            verbose=True
        )
    @agent
    def iteration_supervisor(self) -> Agent:
        return Agent(
            config=self.agents_config['iteration_supervisor'],
            verbose=True
    )

    @task
    def rewrite_task(self) -> Task:
        return Task(
            config=self.tasks_config['rewrite_task'], 
        )

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task']
        )
    @task
    def improvement_task(self)->Task:
        return Task(
            config= self.tasks_config['improvement_task'],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ScriptWriter crew"""
        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
