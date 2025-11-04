"""Experiment management and configuration."""

import yaml
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class ExperimentStatus(Enum):
    """Experiment lifecycle states."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ComparisonOperator(Enum):
    """Success criteria operators."""
    INCREASE = "increase"
    DECREASE = "decrease"
    EQUALS = "equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"


@dataclass
class SuccessCriteria:
    """Define what makes an experiment successful."""
    metric: str
    threshold: float
    operator: ComparisonOperator

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            metric=data['metric'],
            threshold=data['threshold'],
            operator=ComparisonOperator(data['operator'])
        )


@dataclass
class Experiment:
    """YouTube analytics experiment definition."""
    id: str
    name: str
    hypothesis: str
    start_date: str
    end_date: str
    metrics: Dict[str, any]
    success_criteria: SuccessCriteria
    status: ExperimentStatus = ExperimentStatus.DRAFT
    baseline_start: Optional[str] = None
    baseline_end: Optional[str] = None
    video_ids: Optional[Dict[str, List[str]]] = None
    notes: str = ""
    results: Optional[Dict] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @classmethod
    def from_dict(cls, data: Dict):
        """Create experiment from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            hypothesis=data['hypothesis'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            metrics=data['metrics'],
            success_criteria=SuccessCriteria.from_dict(data['success_criteria']),
            status=ExperimentStatus(data.get('status', 'draft')),
            baseline_start=data.get('baseline_start'),
            baseline_end=data.get('baseline_end'),
            video_ids=data.get('video_ids'),
            notes=data.get('notes', ''),
            results=data.get('results'),
            created_at=data.get('created_at', datetime.now().isoformat())
        )

    def to_dict(self) -> Dict:
        """Convert experiment to dictionary for serialisation."""
        result = asdict(self)
        # Use automatic status based on dates
        result['status'] = self.get_automatic_status().value
        result['success_criteria']['operator'] = self.success_criteria.operator.value
        return result

    def get_automatic_status(self) -> ExperimentStatus:
        """
        Determine experiment status automatically based on dates.
        
        Rules:
        - If end_date is in the past → COMPLETED
        - If today is between start_date and end_date → ACTIVE
        - If start_date is in the future → DRAFT
        
        Returns:
            Automatic status based on current date
        """
        today = datetime.now().date()
        start = datetime.fromisoformat(self.start_date).date()
        end = datetime.fromisoformat(self.end_date).date()
        
        if today > end:
            return ExperimentStatus.COMPLETED
        elif start <= today <= end:
            return ExperimentStatus.ACTIVE
        else:  # today < start
            return ExperimentStatus.DRAFT
    
    def is_active(self) -> bool:
        """Check if experiment is currently running based on dates."""
        auto_status = self.get_automatic_status()
        return auto_status == ExperimentStatus.ACTIVE

    def is_ready_for_analysis(self) -> bool:
        """Check if experiment has finished and can be analysed."""
        auto_status = self.get_automatic_status()
        return auto_status == ExperimentStatus.COMPLETED


class ExperimentManager:
    """Manage experiment lifecycle and persistence."""

    def __init__(self, config_file: str = 'experiments.yaml'):
        self.config_file = config_file
        self.experiments: Dict[str, Experiment] = {}
        self.load_experiments()

    def load_experiments(self):
        """Load experiments from YAML configuration."""
        try:
            with open(self.config_file, 'r') as f:
                data = yaml.safe_load(f)

            if not data or 'experiments' not in data:
                self.experiments = {}
                return

            for exp_data in data['experiments']:
                exp = Experiment.from_dict(exp_data)
                self.experiments[exp.id] = exp

        except FileNotFoundError:
            self.experiments = {}

    def save_experiments(self):
        """Save experiments to YAML configuration."""
        data = {
            'experiments': [exp.to_dict() for exp in self.experiments.values()]
        }

        with open(self.config_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def create_experiment(self, experiment: Experiment) -> str:
        """Add new experiment."""
        if experiment.id in self.experiments:
            raise ValueError(f"Experiment {experiment.id} already exists")

        self.experiments[experiment.id] = experiment
        self.save_experiments()
        return experiment.id

    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """Retrieve experiment by ID."""
        return self.experiments.get(experiment_id)

    def list_experiments(self, status: Optional[ExperimentStatus] = None) -> List[Experiment]:
        """List all experiments, optionally filtered by status."""
        experiments = list(self.experiments.values())

        if status:
            experiments = [e for e in experiments if e.status == status]

        return sorted(experiments, key=lambda e: e.created_at, reverse=True)

    def update_experiment(self, experiment_id: str, updates: Dict):
        """Update experiment fields."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")

        exp = self.experiments[experiment_id]

        for key, value in updates.items():
            if hasattr(exp, key):
                setattr(exp, key, value)

        self.save_experiments()

    def update_status(self, experiment_id: str, status: ExperimentStatus):
        """Change experiment status."""
        self.update_experiment(experiment_id, {'status': status})

    def delete_experiment(self, experiment_id: str):
        """Remove experiment."""
        if experiment_id in self.experiments:
            del self.experiments[experiment_id]
            self.save_experiments()

    def get_active_experiments(self) -> List[Experiment]:
        """Get experiments that are currently running."""
        return [e for e in self.experiments.values() if e.is_active()]

    def get_ready_for_analysis(self) -> List[Experiment]:
        """Get experiments that have finished and need analysis."""
        return [e for e in self.experiments.values() if e.is_ready_for_analysis()]
    
    def get_last_successful_experiment(self, before_date: str = None) -> Optional[Experiment]:
        """
        Find the most recent successful experiment.
        
        Args:
            before_date: Optional date (YYYY-MM-DD) to find success before.
                        If provided, only considers experiments that ended before this date.
        
        Returns:
            The most recent successful experiment, or None if no successful experiments exist.
        """
        from datetime import datetime
        
        # Get all completed experiments with results
        completed_experiments = [
            e for e in self.experiments.values()
            if e.results and e.results.get('success') == True
        ]
        
        # Filter by before_date if provided
        if before_date:
            before_dt = datetime.strptime(before_date, '%Y-%m-%d')
            completed_experiments = [
                e for e in completed_experiments
                if datetime.strptime(e.end_date, '%Y-%m-%d') < before_dt
            ]
        
        if not completed_experiments:
            return None
        
        # Sort by end_date (most recent first)
        completed_experiments.sort(
            key=lambda e: datetime.strptime(e.end_date, '%Y-%m-%d'),
            reverse=True
        )
        
        return completed_experiments[0]
