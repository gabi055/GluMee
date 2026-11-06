import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Link } from 'expo-router';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../../../src/firebase';
import { mensajeAuth } from '../../../src/authErrors';
import { e, colorPlaceholder } from '../../../src/estilos';

export default function Login() {
  const [correo, setCorreo] = useState('');
  const [clave, setClave] = useState('');
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);

  async function entrar() {
    setError('');
    if (!correo.trim() || !clave) {
      setError('Escribe tu correo y contraseña.');
      return;
    }
    setCargando(true);
    try {
      await signInWithEmailAndPassword(auth, correo.trim(), clave);
      // La redirección la hace el layout raíz (paso 5)
    } catch (err) {
      setError(mensajeAuth(err));
    } finally {
      setCargando(false);
    }
  }

  return (
    <View style={e.pantalla}>
      <Text style={e.titulo}>Iniciar sesión</Text>
      <TextInput style={e.input} placeholder="Correo" autoCapitalize="none"
        keyboardType="email-address" value={correo} onChangeText={setCorreo} placeholderTextColor={colorPlaceholder}/>
      <TextInput style={e.input} placeholder="Contraseña" secureTextEntry
        value={clave} onChangeText={setClave} placeholderTextColor={colorPlaceholder}/>
      {error ? <Text style={e.error}>{error}</Text> : null}
      <TouchableOpacity style={e.boton} onPress={entrar} disabled={cargando}>
        {cargando ? <ActivityIndicator color="#fff" /> : <Text style={e.botonTexto}>Entrar</Text>}
      </TouchableOpacity>
      <Link href="/(auth)/recuperar" style={e.enlace}>¿Olvidaste tu contraseña?</Link>
      <Link href="/(auth)/registro" style={e.enlace}>Crear cuenta</Link>
    </View>
  );
}