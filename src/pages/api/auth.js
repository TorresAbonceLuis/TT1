import fs from 'fs';
import path from 'path';

const usersFilePath = path.join(process.cwd(), 'src', 'data', 'users.json');

export default function handler(req, res) {
  if (req.method === 'POST') {
    const { email, password, action } = req.body;
    console.log("Datos recibidos:", { email, password, action });

    let users = [];
    if (fs.existsSync(usersFilePath)) {
      const fileContent = fs.readFileSync(usersFilePath, 'utf8').trim();
      if (fileContent) {
        users = JSON.parse(fileContent);
      }
    }

    if (action === 'login') {
      const user = users.find(u => u.email === email && u.password === password);
      if (!user) {
        return res.status(401).json({ message: 'Credenciales incorrectas' });
      }

      console.log("Login exitoso para:", user);
      return res.status(200).json({ message: 'Login exitoso', user });
    }

    if (action === 'register') {
      if (users.find(u => u.email === email)) {
        return res.status(400).json({ message: 'El usuario ya existe' });
      }

      const newUser = { id: users.length + 1, email, password };
      users.push(newUser);
      fs.writeFileSync(usersFilePath, JSON.stringify(users, null, 2));

      console.log("Usuario registrado:", newUser);
      return res.status(201).json({ message: 'Usuario registrado', user: newUser });
    }
  }

  return res.status(405).json({ message: 'Método no permitido' });
}
