import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, Switch } from 'react-native';
import { Link } from 'expo-router';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../../../src/firebase';
import { mensajeAuth } from '../../../src/authErrors';
import { e, colorPlaceholder} from '../../../src/estilos';

export default function Registro() {
  const [correo, setCorreo] = useState('');
  const [clave, setClave] = useState('');
  const [clave2, setClave2] = useState('');
  const [acepta, setAcepta] = useState(false);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);

  async function registrar() {
    setError('');
    if (!correo.trim() || !clave) return setError('Completa todos los campos.');
    if (clave.length < 6) return setError('La contraseña debe tener al menos 6 caracteres.');
    if (clave !== clave2) return setError('Las contraseñas no coinciden.');
    if (!acepta) return setError('Debes aceptar el aviso legal para continuar.');

    setCargando(true);
    try {
      await createUserWithEmailAndPassword(auth, correo.trim(), clave);
      // El layout raíz te lleva a las pestañas (paso 5)
    } catch (err) {
      setError(mensajeAuth(err));
    } finally {
      setCargando(false);
    }
  }

  return (
    <View style={e.pantalla}>
      <Text style={e.titulo}>Crear cuenta</Text>
      <TextInput style={e.input} placeholder="Correo"   placeholderTextColor={colorPlaceholder}
autoCapitalize="none"
        keyboardType="email-address" value={correo} onChangeText={setCorreo} />
      <TextInput style={e.input} placeholder="Contraseña" secureTextEntry
        value={clave} onChangeText={setClave} placeholderTextColor={colorPlaceholder}/>
      <TextInput style={e.input} placeholder="Confirmar contraseña" secureTextEntry
        value={clave2} onChangeText={setClave2} placeholderTextColor={colorPlaceholder} />
      <View style={e.fila}>
        <Switch value={acepta} onValueChange={setAcepta} />
        <Text style={e.legal}>
          Entiendo que GluMee es informativa: no diagnostica, no indica dosis de medicamentos
          ni sustituye la atención de un profesional de la salud.
        </Text>
      </View>
      {error ? <Text style={e.error}>{error}</Text> : null}
      <TouchableOpacity style={e.boton} onPress={registrar} disabled={cargando}>
        {cargando ? <ActivityIndicator color="#ffffff" /> : <Text style={e.botonTexto}>Crear cuenta</Text>}
      </TouchableOpacity>
      <Link href="/(auth)/login" style={e.enlace}>Ya tengo cuenta</Link>
    </View>
  );
}