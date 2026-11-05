import { StyleSheet } from 'react-native';
export const colorPlaceholder = '#9AA0A6';
export const e = StyleSheet.create({
  pantalla: { flex: 1, justifyContent: 'center', padding: 24, backgroundColor: '#fff' },
  titulo: { fontSize: 28, fontWeight: '700', marginBottom: 24 },
  input: {
    borderWidth: 1, borderColor: '#ccc', borderRadius: 8,
    padding: 12, marginBottom: 12, fontSize: 16,
  },
  boton: { backgroundColor: '#2f7d6d', padding: 14, borderRadius: 8, alignItems: 'center', marginTop: 4 },
  botonTexto: { color: '#fff', fontSize: 16, fontWeight: '600' },
  error: { color: '#b00020', marginBottom: 12 },
  info: { color: '#2f7d6d', marginBottom: 12 },
  enlace: { color: '#2f7d6d', textAlign: 'center', marginTop: 16 },
  legal: { fontSize: 13, color: '#555', flex: 1 },
  fila: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 12 },
});