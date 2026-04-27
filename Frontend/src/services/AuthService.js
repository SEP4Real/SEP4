export async function register(data) {
  console.log("Sending to backend:", data);

  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ ok: true });
    }, 500);
  });
}