use serde_json::Value;
use std::{fs, path::{Path,PathBuf}, process::Command};

fn forbidden() -> String { ["ORESoftware", "/", "project-registry"].concat() }
fn safe_registry(text:&str)->bool {
    let Ok(g)=serde_json::from_str::<Value>(text) else {return true};
    if g.get("audience").and_then(Value::as_str)!=Some("public") {return true}
    if g.get("generated").and_then(|v|v.get("managed_by")).and_then(Value::as_str)!=Some("ore-repository-relationship-rollout"){return true}
    g.get("private_registry").and_then(|v|v.get("repository")).and_then(Value::as_str)==Some("approved-private-registry")
}
fn tracked(root:&Path)->Result<Vec<PathBuf>,String>{
    let out=Command::new("git").args(["ls-files","-z"]).current_dir(root).output().map_err(|e|e.to_string())?;
    if !out.status.success(){return Err(format!("git ls-files failed: {}",String::from_utf8_lossy(&out.stderr)))}
    out.stdout.split(|b|*b==0).filter(|b|!b.is_empty()).map(|b|
        std::str::from_utf8(b).map(|p|root.join(p)).map_err(|e|format!("tracked file encoding: {e}"))
    ).collect()
}
fn validate(root:&Path)->Result<Vec<String>,String>{
    let mut errors=Vec::new();
    let needle=forbidden();
    for path in tracked(root)? {
        let name=path.strip_prefix(root).map_err(|e|e.to_string())?.display().to_string();
        let meta=fs::symlink_metadata(&path).map_err(|e|format!("{name}: {e}"))?;
        let text=if meta.file_type().is_symlink(){
            fs::read_link(&path).map_err(|e|format!("{name}: {e}"))?
                .to_str().ok_or_else(||format!("{name}: non-UTF-8 link"))?.to_owned()
        }else{
            let bytes=fs::read(&path).map_err(|e|format!("{name}: {e}"))?;
            match String::from_utf8(bytes){Ok(t)=>t,Err(_)=>continue}
        };
        if text.contains(&needle){errors.push(format!("private repository reference in {name}"))}
        if path.file_name().and_then(|v|v.to_str())==Some("repository-relationships.json")&&!safe_registry(&text){
            errors.push(format!("non-opaque private registry locator in {name}"))
        }
    }
    Ok(errors)
}
fn main(){
    let mut args=std::env::args();
    let _=args.next();
    let root=args.next().unwrap_or_else(||".".to_owned());
    if args.next().is_some(){eprintln!("usage: public-privacy-validator [root | --self-test]");std::process::exit(2)}
    if root=="--self-test"{
        assert!(forbidden().contains("project-registry"));
        assert!(!"approved-private-registry".contains(&forbidden()));
        assert!(!safe_registry(r#"{"audience":"public","generated":{"managed_by":"ore-repository-relationship-rollout"},"private_registry":{"repository":"unsafe"}}"#));
        println!("Public privacy validator self-test passed.");
        return
    }
    let root=fs::canonicalize(&root).unwrap_or_else(|e|{eprintln!("ERROR: {e}");std::process::exit(2)});
    match validate(&root){
        Ok(errors) if errors.is_empty()=>println!("Public privacy validation passed."),
        Ok(errors)=>{for e in errors{eprintln!("ERROR: {e}")}std::process::exit(1)},
        Err(e)=>{eprintln!("ERROR: {e}");std::process::exit(2)}
    }
}
#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn forbidden_reference_is_detected(){
        assert!(format!("{}/{}","ORESoftware","project-registry").contains(&forbidden()));
    }
    #[test]fn public_registry_locator_must_be_opaque(){
        assert!(!safe_registry(r#"{"audience":"public","generated":{"managed_by":"ore-repository-relationship-rollout"},"private_registry":{"repository":"exposed"}}"#));
        assert!(safe_registry(r#"{"audience":"public","generated":{"managed_by":"ore-repository-relationship-rollout"},"private_registry":{"repository":"approved-private-registry"}}"#));
    }
    #[test]fn other_audience_and_invalid_json_preserve_legacy_behavior(){
        assert!(safe_registry(r#"{"audience":"private","private_registry":{"repository":"exposed"}}"#));
        assert!(safe_registry("{"));
    }
}
