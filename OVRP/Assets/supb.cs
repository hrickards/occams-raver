using UnityEngine;
using System.Collections;

public class supb : MonoBehaviour {
	protected Vector3 V;
	protected Vector3[] prev = new Vector3[40];
	protected int init; protected float gx,gy;
	protected bool back;
	protected OVRCameraController occ = null;
	protected Animation ass=null;
	
	// Use this for initialization
	void Start () {
		init = 0;
		ass=GetComponent<Animation>();
		ass.Stop();
	}
	// Update is called once per frame
	void Update () 
	{
		OVRCameraController[] CameraControllers;
		CameraControllers = FindObjectsOfType(typeof(OVRCameraController)) as OVRCameraController[];
		
		if(CameraControllers.Length == 0)
			Debug.LogWarning("OVRPlayerController: No OVRCameraController attached.");
		else if (CameraControllers.Length > 1)
			Debug.LogWarning("OVRPlayerController: More then 1 OVRCameraController attached.");
		else occ = CameraControllers[0];	
		if (init < 20) 
		{
			
			occ.GetCameraOrientationEulerAngles (ref prev[init++]);
		}
		else 
		{
			ass=GetComponent<Animation>();
			ass.Stop();
			V = new Vector3 (0, 0, 0);
			occ.GetCameraOrientationEulerAngles (ref V);
			float dx=prev[0].x-V.x,dy=prev[0].y-V.y,dz=prev[0].z-V.z;
			float tot=Mathf.Sqrt(dx*dx+dy*dy);
			if(float.IsNaN(tot)) tot=0;
			for(int i=0;i<19;i++) prev[i]=prev[i+1];
			init--;
			if(tot<30) return;
			float R=4;
			dx=R*Mathf.Sin(dx);
			dy=R*Mathf.Sin(dy);
			//print (dx+" "+dy);
			if(back)
			{
				print (tot+"   "+((dx*gx+dy*gy)/Mathf.Sqrt(gx*gx+gy*gy)));
				if(((dx*gx+dy*gy)/Mathf.Sqrt(gx*gx+gy*gy))<1.5) return;
				dx=gx; dy=gy;
				back=false;
			}
			else
			{
				gx=-dx;gy=-dy;
				back=true;
			}
			init=0; 
			this.transform.Translate(dx,dy,0);
			ass.Play();

		}
	}
}