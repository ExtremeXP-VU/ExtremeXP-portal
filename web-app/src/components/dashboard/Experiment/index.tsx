import './style.scss';
import { useState, useEffect, useCallback } from 'react';
import useRequest from '../../../hooks/useRequest';
import { message } from '../../../utils/message';
import { timestampToDate, timeNow } from '../../../utils/timeToDate';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  downloadGraphicalModel,
  uploadGraphicalModel,
} from '../../../utils/fileIO';
import Popover from '../../general/Popover';
import {
  GraphicalModelType,
  WorkflowType,
  defaultWorkflow,
} from '../../../types/workflows';
import {
  WorkflowsResponseType,
  CreateWorkflowResponseType,
  UpdateWorkflowNameResponseType,
  DeleteWorkflowResponseType,
} from '../../../types/requests';

const Project = () => {
  const [experiments, setExperiments] = useState([defaultWorkflow]);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [newExpName, setNewExpName] = useState('');

  const [showPopover, setShowPopover] = useState(false);
  const [deleteIndex, setDeleteIndex] = useState<number | null>(null);

  const isExperimentEmpty = experiments.length === 0;

  // make sure the expID is the same as the one in the url
  const projID = useLocation().pathname.split('/')[3];

  const { request: experimentsRequest } = useRequest<WorkflowsResponseType>();
  const { request: createExperimentRequest } =
    useRequest<CreateWorkflowResponseType>();
  const { request: updateExpNameRequest } =
    useRequest<UpdateWorkflowNameResponseType>();
  const { request: deleteExperimentRequest } =
    useRequest<DeleteWorkflowResponseType>();

  const navigate = useNavigate();

  const getExperiments = useCallback(() => {
    experimentsRequest({
      url: `work/projects/${projID}/experiments`,
    })
      .then((data) => {
        if (data.data.workflows) {
          const workflows = data.data.workflows;
          setExperiments(workflows);
        }
      })
      .catch((error) => {
        if (error.message) {
          message(error.message);
        }
      });
  }, [experimentsRequest, projID]);

  useEffect(() => {
    getExperiments();
  }, [getExperiments]);

  const postNewExperiment = useCallback(
    (name: string, graphicalModel: GraphicalModelType) => {
      createExperimentRequest({
        url: `/work/projects/${projID}/workflows/create`,
        method: 'POST',
        data: {
          work_name: name,
          graphical_model: graphicalModel,
        },
      })
        .then(() => {
          getExperiments();
        })
        .catch((error) => {
          if (error.message) {
            message(error.message);
          }
        });
    },
    [projID, createExperimentRequest, getExperiments]
  );

  const handleNewExperiment = () => {
    postNewExperiment(`experiment-${timeNow()}`, {
      nodes: [],
      edges: [],
    });
  };

  const handleStartEditingName = (index: number) => {
    setNewExpName(experiments[index].name);
    if (editingIndex === null) {
      setEditingIndex(index);
    } else {
      setEditingIndex(null);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (editingIndex === null) return;
      if (newExpName === '' || newExpName === experiments[editingIndex].name) {
        setEditingIndex(null);
        return;
      }
      renameExperiment();
      setEditingIndex(null);
    }
  };

  const renameExperiment = () => {
    if (newExpName === '' || editingIndex === null) return;
    if (newExpName === experiments[editingIndex].name) return;
    if (newExpName.length > 35) {
      message('The length of the name should be less than 35 characters.');
      return;
    }
    updateExpNameRequest({
      url: `/work/projects/${projID}/workflows/${
        experiments[editingIndex!].id_workflow
      }/update/name`,
      method: 'PUT',
      data: {
        work_name: newExpName,
      },
    })
      .then(() => {
        getExperiments();
      })
      .catch((error) => {
        message(error.response.data?.message || error.message);
      });
  };

  const handleDownloadExperiment = (index: number) => {
    downloadGraphicalModel(
      experiments[index].graphical_model,
      experiments[index].name
    );
  };

  const handleOpenExperiment = (experiment: WorkflowType) => {
    navigate(`/editor/experiment/${projID}/${experiment.id_workflow}`);
  };

  const handleAnalyzeExperiment = (experiment: WorkflowType) => {
    window.open(`https://extreme-viz.pulsar.imsi.athenarc.gr/${experiment.id_workflow}`, '_blank', 'noopener,noreferrer');
  }

  function handleOpenPopover(index: number) {
    setDeleteIndex(index);
    setShowPopover(true);
  }

  function closeMask() {
    setShowPopover(false);
    setDeleteIndex(null);
  }

  function handleCancelDelete() {
    closeMask();
  }

  const handleDeleteExperiment = () => {
    if (deleteIndex === null) return;
    deleteExperimentRequest({
      url: `/work/projects/${projID}/workflows/${experiments[deleteIndex].id_workflow}/delete`,
      method: 'DELETE',
    })
      .then(() => {
        getExperiments();
      })
      .catch((error) => {
        message(error.response.data?.message || error.message);
      });
    closeMask();
  };

  async function handleImportExperiment() {
    const model = await uploadGraphicalModel();
    if (!model) {
      return;
    }
    postNewExperiment(`imported-experiment-${timeNow()}`, model);
  }

  return (
    <div className="specification">
      <div className="specification__functions">
        <button
          className="specification__functions__new"
          onClick={handleNewExperiment}
        >
          new workflow
        </button>
        <button
          className="specification__functions__import"
          onClick={handleImportExperiment}
        >
          import workflow
        </button>
      </div>
      <div className="specification__contents">
        <div className="specification__contents__header">
          <div className="specification__contents__header__title">
            Workflow
          </div>
          <div className="specification__contents__header__create">
            Created At
          </div>
          <div className="specification__contents__header__update">
            Updated At
          </div>
          <div className="specification__contents__header__operations"></div>
        </div>
        {isExperimentEmpty ? (
          <div className="specification__contents__empty">
            <span className="iconfont">&#xe6a6;</span>
            <p>Empty Workflows</p>
          </div>
        ) : (
          <ul className="specification__contents__list">
            {experiments.map((specification, index) => (
              <li className="specification__contents__list__item" key={index}>
                <div className="specification__contents__list__item__title">
                  <span
                    title="modify the name"
                    className="iconfont editable"
                    onClick={() => handleStartEditingName(index)}
                  >
                    &#xe63c;
                  </span>
                  {editingIndex === index ? (
                    <input
                      type="text"
                      value={newExpName}
                      onChange={(e) => setNewExpName(e.target.value)}
                      onKeyUp={handleKeyPress}
                    />
                  ) : (
                    <p>{specification.name}</p>
                  )}
                </div>
                <div className="specification__contents__list__item__create">
                  {timestampToDate(specification.create_at)}
                </div>
                <div className="specification__contents__list__item__update">
                  {timestampToDate(specification.update_at)}
                </div>
                <div className="specification__contents__list__item__operations">
                  <span
                    title="download graphical model"
                    className="iconfont editable"
                    onClick={() => handleDownloadExperiment(index)}
                  >
                    &#xe627;
                  </span>
                  <span
                    title="delete this specification"
                    className="iconfont editable"
                    onClick={() => handleOpenPopover(index)}
                  >
                    &#xe634;
                  </span>
                  <button
                    title="open specification in the graphical editor"
                    onClick={() => {
                      handleOpenExperiment(specification);
                    }}
                  >
                    open
                  </button>
                  <button
                    className="analyze_button"
                    title="analyze experiment"
                    onClick={() => {
                      handleAnalyzeExperiment(specification);
                    }}
                  >
                    analyze
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      <Popover show={showPopover} blankClickCallback={closeMask}>
        <div className="popover__delete">
          <div className="popover__delete__text">
            {`Do you want to delete ${
              deleteIndex ? experiments[deleteIndex].name : 'the specification'
            }?`}
          </div>
          <div className="popover__delete__buttons">
            <button
              className="popover__delete__buttons__cancel"
              onClick={handleCancelDelete}
            >
              cancel
            </button>
            <button
              className="popover__delete__buttons__confirm"
              onClick={handleDeleteExperiment}
            >
              confirm
            </button>
          </div>
        </div>
      </Popover>
    </div>
  );
};

export default Project;
