import { createBrowserRouter, RouterProvider } from "react-router-dom";

import Root from "./components/Root";
import Error from "./pages/Error";
import Dashboard from "./pages/Dashboard";
import Resumes from "./pages/Resumes";
import Queue from "./pages/Queue";
import Jobs from "./pages/Jobs";
import {
  RecoilRoot,
} from "recoil";
import JobDescription from "./pages/JobDescription";
import ResumeDescription from "./pages/ResumeDescription";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Root />,
    errorElement: <Error />,
    children: [
      {
        path: "dashboard",
        element: <Dashboard />,
      },
      {
        path: "queue",
        element: <Queue />,
      },
      {
        path: "resumes",
        element: <Resumes />,
      },
      {
        path: "resumes/:id",
        element: <ResumeDescription />,
      },
      {
        path: "jobs",
        element: <Jobs />,
      },
      {
        path: "jobs/:id",
        element: <JobDescription />,
      },
    ],
  },
]);

function App() {
  return (
    <RecoilRoot>
      <RouterProvider router={router} />
    </RecoilRoot>
  );
}

export default App;
