import { useState, useEffect } from "react";
import Login from "./components/Login";
import Register from "./components/Register";

//controls which page is shown and manages logged in user state
function App() {

  // page state: determines whether to show login or register
  const [page, setPage] = useState("login");

  // user state: stores currently logged in user
  const [user, setUser] = useState(null);

  // runs once when app loads -- checks if a user is stored in localstorage
  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    const token = localStorage.getItem("token");

    // if user and token exist, set it in state
    if (savedUser && token) {
      setUser(savedUser);
    }
  }, []);

  return (
    <>
      {/* if user is logged in, show dashboard */}
      {user ? (
        <>
          {/* display username */}
          <h1>
            Welcome {user.charAt(0).toUpperCase() + user.slice(1)}
          </h1>

          {/* logout button */}
          <button
            onClick={() => {
              // remove user and token from localstorage
              localStorage.removeItem("user");
              localStorage.removeItem("token");

              // reset user state -- returns to login/register view
              setUser(null);
            }}
          >
            Logout
          </button>
        </>
      ) : (
        <>
          {/* show login page */}
          {page === "login" && (
            <Login
              // switch to register page
              goToRegister={() => setPage("register")}

              // pass setUser so login can update global user state
              setUser={setUser}
            />
          )}

          {/* show register page */}
          {page === "register" && (
            <Register
              // switch back to login after registering
              goToLogin={() => setPage("login")}
            />
          )}
        </>
      )}
    </>
  );
}

export default App;