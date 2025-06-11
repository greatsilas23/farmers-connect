import React, { useState, useRef } from "react";
import { useAuth } from "../hooks/Auth";
import { notify } from "../hooks/Notification";
import { useNavigate } from "react-router-dom";

function Register() {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [first_name, setFirstName] = useState("");
  const [last_name, setLastName] = useState("");
  const [is_farmer, setIsFarmer] = useState(false);
  const { register } = useAuth();

  const passwordRef = useRef(null);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (loading) return;
    setLoading(true);

    if (!email || !password || !first_name || !last_name) {
      notify("error", "All fields are required");
      setLoading(false);
      return;
    }

    let data = await register(email, first_name, last_name, password, is_farmer);
    if (data) {
      notify("success", "Registration successful");
      navigate("/login");
    }

    setLoading(false);
  };

  return (
    <div id="content">
      <div className="container">
        <div className="col-md-12">
          <ul className="breadcrumb">
            <li>
              <a href="/">Home</a>
            </li>
            <li>Register</li>
          </ul>
        </div>
        <div className="col-md-12">
          <div className="box">
            <div className="box-header">
              <center>
                <h2>Register a new account</h2>
              </center>
              <form onSubmit={handleSubmit} encType="multipart/form-data">
                <div className="form-group">
                  <label>First Name</label>
                  <input
                    type="text"
                    className="form-control"
                    name="first_name"
                    placeholder="Enter Your First Name"
                    required
                    autoComplete="on"
                    onChange={(e) => setFirstName(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Last Name</label>
                  <input
                    type="text"
                    className="form-control"
                    name="last_name"
                    placeholder="Enter Your Last Name"
                    required
                    autoComplete="on"
                    onChange={(e) => setLastName(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Your E-mail</label>
                  <input
                    type="email"
                    className="form-control"
                    name="email"
                    placeholder="Enter Your E-mail"
                    required
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="gap-6">
                    Your Password
                    <span
                      onClick={() => {
                        if (passwordRef.current.type === "password") {
                          passwordRef.current.type = "text";
                        } else {
                          passwordRef.current.type = "password";
                        }
                      }}
                      className="bg-primary text-white px-1 rounded"
                      style={{ cursor: "pointer", marginLeft: "10px" }}
                    >
                      Show Password
                    </span>
                  </label>
                  <input
                    ref={passwordRef}
                    type="password"
                    className="form-control"
                    name="password"
                    placeholder="Enter Password"
                    required
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id="farmerCheckBox"
                    onChange={(e) => setIsFarmer(e.target.checked)}
                  />
                  <label
                    className="form-check-label ml-4 px-4"
                    htmlFor="farmerCheckBox"
                  >
                    Are you a farmer?
                  </label>
                </div>

                <div className="text-center" style={{ marginTop: "20px" }}>
                  <button
                    className="btn btn-primary"
                    type="submit"
                    name="register"
                    disabled={loading}
                  >
                    {loading ? (
                      <span>
                        <i className="fa fa-spinner fa-pulse"></i> Loading......
                      </span>
                    ) : (
                      <span>
                        <i className="fa fa-user-md"></i> Register
                      </span>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;
