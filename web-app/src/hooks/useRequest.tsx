import { useState, useRef, useCallback } from 'react';
import axios, { AxiosRequestConfig } from 'axios';
import { useNavigate } from 'react-router-dom';

import { useAccountStore, logout } from '../stores/accountStore';

// Get the token from localStorage and add it to the request headers

const defaultRequestConfig: AxiosRequestConfig = {
  url: '/',
  method: 'GET',
  data: {},
};

function useRequest<T>(options: AxiosRequestConfig = defaultRequestConfig) {
  const navigate = useNavigate();
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState(null);
  const [loaded, setLoaded] = useState(false);
  const controllerRef = useRef(new AbortController()); // AbortController is used to cancel the request

  axios.defaults.headers.common['Access-Control-Allow-Origin'] = '*';
  axios.defaults.headers.common['Authorization'] = `Bearer ${useAccountStore.getState().token}`;

  const cancelRequest = () => {
    controllerRef.current.abort();
  };

  const request = useCallback(
    (requestOptions?: AxiosRequestConfig) => {
      // Reset state
      setData(null);
      setError(null);
      setLoaded(false);

      const loginToken = useAccountStore.getState();
      // const params = loginToken ? { token: loginToken } : {};
      const params = {};
      console.log('useRequest->loginToken', loginToken.token);

      let scope = "ReadData";
      if (requestOptions?.method === 'POST' || requestOptions?.method === 'PUT' || requestOptions?.method === 'DELETE') {
        scope = "WriteData";
      }

      return axios
        .request<T>({
          baseURL: import.meta.env.VITE_API_URL,
          url: requestOptions?.url || '',
          method: requestOptions?.method || options.method,
          signal: controllerRef.current.signal,
          params: { ...params, ...requestOptions?.params },
          data: requestOptions?.data || options.data,
          headers: {
            Authorization: `Bearer ${loginToken.token}`,
            'Authorization-Scope': scope,
          }
        })
        .then((response) => {
          setData(response.data);
          return response.data;
        })
        .catch((error) => {
          if (error?.response?.status === 403) {
            logout();
            navigate('/account/login');
          }
          setError(error);
          throw error;
        })
        .finally(() => {
          setLoaded(true);
        });
    },
    [navigate, options]
  );

  return { data, error, loaded, request, cancelRequest };
}

export default useRequest;
