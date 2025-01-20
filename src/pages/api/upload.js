import formidable from "formidable";
import fs from "fs";
import path from "path";

export const config = {
  api: {
    bodyParser: false, // Necesario para manejar archivos correctamente con formidable
  },
};

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ message: "Método no permitido" });
  }

  const form = formidable({ // ✅ Nueva forma de crear el objeto formidable en v2+
    uploadDir: path.join(process.cwd(), "public/uploads"),
    keepExtensions: true,
    multiples: false,
  });

  form.parse(req, async (err, fields, files) => {
    if (err) {
      return res.status(500).json({ message: "Error al procesar el archivo" });
    }

    const file = files.file[0];
    const newPath = path.join(form.uploadDir, file.originalFilename);

    fs.renameSync(file.filepath, newPath);

    return res.status(200).json({
      message: "Archivo subido correctamente",
      filePath: `/uploads/${file.originalFilename}`,
    });
  });
}
