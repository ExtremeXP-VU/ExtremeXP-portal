import './style.scss';

import { Link, useNavigate, Outlet, useLocation } from 'react-router-dom';
import { logout } from '../../stores/accountStore';

const Repository = () => {
  const location = useLocation();
  const isExperiments = location.pathname.includes('/projects');
  const isTask = location.pathname.includes('/categories');
  const isDatasets = location.pathname.includes('/organizations');
<<<<<<< HEAD
  const isProgress = location.pathname.includes('/progress');
  const experimentSelectedClass = isExperiments ? 'selected' : '';
  const taskSelectedClass = isTask ? 'selected' : '';
  const datasetSelectedClass = isDatasets ? 'selected' : '';
  const progressSelectedClass = isProgress ? 'selected' : '';
=======
  const experimentSelectedClass = isExperiments ? 'selected' : '';
  const taskSelectedClass = isTask ? 'selected' : '';
  const datasetSelectedClass = isDatasets ? 'selected' : '';
>>>>>>> 938b764 (Added dataset functionalities)

  const navigate = useNavigate();

  const handleSignOut = () => {
    logout();
    navigate('/account/login');
  };

  return (
    <div className="page repository">
      <div className="repository__panel">
        <div className="repository__panel__header">
          <span>Dashboard</span>
        </div>
        <div className="repository__panel__items">
          <Link to={'/dashboard/projects'}>
            <div
              className={`repository__panel__items__item ${experimentSelectedClass}`}
            >
              <span className="iconfont">&#xe6cf;</span>
              <p>Experiments</p>
            </div>
          </Link>
          <Link to={'/dashboard/categories'}>
            <div
              className={`repository__panel__items__item ${taskSelectedClass}`}
            >
              <span className="iconfont">&#xe610;</span>
              <p>Templates</p>
            </div>
          </Link>
          <Link to={'/dashboard/organizations'}>
            <div
                className={`repository__panel__items__item ${datasetSelectedClass}`}
            >
              <span className="iconfont">&#xea2a;</span>
              <p>Datasets</p>
            </div>
          </Link>
<<<<<<< HEAD
          <Link to={'/dashboard/progress'}>
            <div
                className={`repository__panel__items__item ${progressSelectedClass}`}
            >
              <span className="iconfont">&#xe653;</span>
              <p>Progress</p>
            </div>
          </Link>
=======
>>>>>>> 938b764 (Added dataset functionalities)
        </div>
        <div className="repository__panel__sign-out">
          <button
            className="repository__panel__sign-out__button"
            onClick={handleSignOut}
          >
            <span className="iconfont">&#xe6a5;</span>
            <span>sign out</span>
          </button>
        </div>
      </div>
      <div className="repository__content">
        <Outlet />
      </div>
    </div>
  );
};

export default Repository;
