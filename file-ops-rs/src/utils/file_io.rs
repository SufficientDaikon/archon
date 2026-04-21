pub struct FileIo;

impl FileIo {
    pub fn read_file_lines(_path: &str) -> crate::errors::Result<(Vec<String>, String, String)> {
        Ok((vec![], "utf-8".to_string(), "\n".to_string()))
    }
}
