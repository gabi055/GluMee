import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Link } from 'expo-router';
import { sendPasswordResetEmail } from 'firebase/auth';
import { auth } from '../../../src/firebase';
import { mensajeAuth } from '../../../src/authErrors';
import { e } from '../../../src/estilos';

export default function Recuperar() {
  const [correo, setCorreo] = useState('');
  const [error, setError] = useState('');
  const [aviso, setAviso] = useState('');
  const [cargando, setCargando] = useState(false);

  async function enviar() {
    setError('');
    setAviso('');
    if (!correo.trim()) return setError('Escribe tu correo.');
    setCargando(true);
    try {
      await sendPasswordResetEmail(auth, correo.trim());
      setAviso('Si el correo tiene una cuenta, recibirás un enlace para restablecer tu contraseña. Revisa también spam.');
    } catch (err) {
      setError(mensajeAuth(err));
    } finally {
      setCargando(false);
    }
  }

  return (
    <View style={e.pantalla}>
      <Text style={e.titulo}>Recuperar contraseña</Text>
      <TextInput style={e.input} placeholder="Correo" autoCapitalize="none"
        keyboardType="email-address" value={correo} onChangeText={setCorreo} />
      {error ? <Text style={e.error}>{error}</Text> : null}
      {aviso ? <Text style={e.info}>{aviso}</Text> : null}
      <TouchableOpacity style={e.boton} onPress={enviar} disabled={cargando}>
        {cargando ? <ActivityIndicator color="#fff" /> : <Text style={e.botonTexto}>Enviar enlace</Text>}
      </TouchableOpacity>
      <Link href="/(auth)/login" style={e.enlace}>Volver a iniciar sesión</Link>
    </View>
  );
}