export interface HyperParameter {
  id?: string;
  name: string;
  type: 'number' | 'categorical' | 'boolean';
  default: number | string | boolean;
  range?: [number, number];
  options?: string[];
  values?: number[];
  inputType?: 'range' | 'enumeration';
}

export interface Task {
  id: string;
  name: string;
  type: 'dataset' | 'algorithm' | 'preprocessing' | 'evaluation';
  hyperParameters: HyperParameter[];
  selected: boolean;
  implementationRef?: string;
  description?: string;
  isAbstract?: boolean;
}

export interface Step {
  id: string;
  name: string;
  type: 'dataset' | 'algorithm' | 'preprocessing' | 'evaluation';
  tasks: Task[];
  subSteps?: Step[];
  collapsed?: boolean;
  hyperParameterTuningEnabled?: boolean;
  gridSearchEnabled?: boolean;
}

export interface SearchOption {
  id: string;
  paramId: string;
  min?: number;
  max?: number;
  values?: number[];
  inputType: 'range' | 'enumeration';
}

export interface Space {
  id: string;
  name: string;
  steps: Step[];
  collapsed?: boolean;
  status: 'idle' | 'running' | 'completed' | 'error';
  executionTime?: number;
  gridSearchEnabled?: boolean;
  searchMethod?: SearchMethod;
  searchOptions?: SearchOption[];
  workflow?: SavedWorkflow;
}

export interface Node {
  id: string;
  name: string;
  type: 'container' | 'task';
  spaces: Space[];
  collapsed?: boolean;
  status: 'idle' | 'running' | 'completed' | 'error';
  executionOrder: number;
  data?: {
    variants: {
      id_task: string;
      name: string;
      implementationRef: string;
      isAbstract: boolean;
      parameters: {
        id: string;
        name: string;
        type: string;
        values: number[];
      }[];
      description: string;
    }[];
  };
}

export type SearchMethod = 'grid' | 'random' | 'bayesian' | 'evolutionary';

export interface WorkflowStep extends Step {
  onRemove?: (id: string) => void;
  onSelectTask?: (stepId: string, taskId: string) => void;
}

export interface SavedWorkflow {
  id: string;
  name: string;
  description: string;
  steps: Step[];
  createdAt: string;
  nodes?: Node[];
}

export interface StepSelectorProps {
  algorithms: Step[];
  datasets: Step[];
  preprocessing: Step[];
  onSelect: (step: Step) => void;
  onClose?: () => void;
}

export interface ImportWorkflowModalProps {
  onClose: () => void;
  onImport: (workflow: SavedWorkflow) => void;
}

export interface ExperimentSave {
  id: string;
  name: string;
  project_id?: string;
  created_at?: number;
  updated_at?: number;
  steps: ExperimentStep[];
}

export interface ExperimentStep {
  id: string;
  name: string;
  type: string;
  executionOrder?: number;
  collapsed?: boolean;
  status?: 'idle' | 'running' | 'completed' | 'error';
  spaces: ExperimentSpace[];
}

export interface ExperimentSpace {
  id: string;
  name: string;
  status?: 'idle' | 'running' | 'completed' | 'error';
  collapsed?: boolean;
  gridSearchEnabled?: boolean;
  searchMethod?: 'grid' | 'random' | 'bayesian' | 'evolutionary';
  workflow_id?: string; // Reference to imported workflow
  // If you still support steps/tasks in a space, you can add:
  // steps?: WorkflowStep[];
}
