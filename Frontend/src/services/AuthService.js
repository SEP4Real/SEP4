export async function register(data) {
  console.log("Sending to backend:", data);

  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ ok: true });
    }, 500);
  });
}
export async function login(data) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (data.email === "test@test.com" && data.password === "123") {
        resolve({
          user: {
            email: data.email,
            name: "Test User",
          },
        });
      } else {
        reject(new Error("Invalid credentials"));
      }
    }, 500);
  });
}