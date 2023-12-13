import { useNavigate } from "react-router-dom";
import { useState } from "react";
import useRequest from "../../hooks/useRequest";

import { message } from "../../utils/message";

type ResponseType = {
  message: string;
  data: {
    jwt: string;
  };
};

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const { request } = useRequest<ResponseType>();

  const navigate = useNavigate();

  const handleLogin = () => {
    if (!username || !password) return message("username or password is empty");

    request({
      url: `users/login`,
      method: "POST",
      data: {
        username: username,
        password: password,
      },
    })
      .then((response) => {
        if (response.data.jwt) {
          localStorage.setItem("token", response.data.jwt);
          localStorage.setItem("username", username);
          navigate(`/repository/${username}/experiments`);
        }
      })
      .catch((error) => {
        message(error.response.data?.message || "unknown error");
      });
  };

  return (
    <>
      <div className="login__form">
        <div className="login__form__item">
          <div className="login__form__item__title"> username </div>
          <input
            id="username"
            className="login__form__item__content"
            type="text"
            placeholder="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="login__form__item">
          <div className="login__form__item__title"> password </div>
          <input
            id="password"
            className="login__form__item__content"
            type="password"
            placeholder="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
      </div>
      <button className="login__submit" onClick={handleLogin}>
        LOGIN
      </button>
    </>
  );
};

export default Login;